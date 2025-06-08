import uuid
from fastapi import FastAPI, File, Request, UploadFile
from pydantic import BaseModel
from helpers.helpers_func import get_priority
from helpers.queue import queue_doc_task, queue_link_task
from helpers.middleware import JWTMiddleware

from fastapi.responses import Response
from fastapi.exceptions import HTTPException
from helpers.mongo_connect import mongo_find_one
from helpers.jwt_utils import create_token
from helpers.password_utils import verify_password
from datetime import timedelta

from helpers.storage import upload_to_gcs

class Message(BaseModel):
    message: str
    doc_id: str
    link_id: str

class LoginRequest(BaseModel):
    username: str
    password: str

app = FastAPI()
# app.add_middleware(JWTMiddleware)


@app.get("/")
def read_root():
    return {"status": "server is up and running"}

@app.post("/login")
def login(data: LoginRequest, response: Response):
    if data.password == "" or data.username == "":
        raise HTTPException(status_code=401, detail="Invalid username or password")

    user = mongo_find_one({"username": data.username}, "users")
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    if not verify_password(data.password, user.get("password")):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    token = create_token({"sub": user.get("_id")}, timedelta(days=1))

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=True,
        samesite="Lax",
        max_age=86400,
        path="/",
    )

    return {"message": "Logged in, token set in cookie", "success": True}

@app.get("/user")
def user(response: Response):
    return {"message": "User is logged in", "success": True}

 
@app.post("/chat")
def chat(message: Message):
    return {"status": "success"}

@app.post("/upload")
def upload(request: Request, file: UploadFile = File(...)):
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="user not logged in")
    file.file.seek(0)
    # upload document to google drive and return file_id
    file_id = upload_to_gcs(file.file, file.filename)
    
    # queue document task
    job_id = uuid.uuid4()
    priority = get_priority(user.get("plan"))
    if not queue_doc_task(user.get("_id"), job_id, priority, file_id):
        raise HTTPException(status_code=500, detail="Failed to queue document")
    
    return {"status": "success", "job_id": job_id}

@app.post("/link")
def link(request: Request, message: Message):
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="user not logged in")
    
    priority = get_priority(user.get("plan"))
    job_id = uuid.uuid4()
    if not queue_link_task(user.get("_id"), job_id, priority, message.message):
        raise HTTPException(status_code=500, detail="Failed to queue document")
    return {"status": "success", "job_id": job_id}

@app.get("/status/{id}")
def get_status(id: str):
    
    return {"status": "success"}