import os
import uuid
from fastapi import FastAPI, File, Request, UploadFile
from helpers.redis import redis_queue_get_data
from pydantic import BaseModel
from helpers.helpers_func import get_priority
from helpers.queue import queue_task_helper
from helpers.middleware import JWTMiddleware

from fastapi.responses import Response
from fastapi.exceptions import HTTPException
from helpers.mongo_connect import mongo_create_one, mongo_find_one
from helpers.jwt_utils import create_token
from helpers.password_utils import hash_password, verify_password
from datetime import timedelta
from fastapi.middleware.cors import CORSMiddleware
from helpers.storage import upload_to_gcs


class Message(BaseModel):
    message: str
    doc_id: str
class LinkMessage(BaseModel):
    message: str

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str

app = FastAPI()
app.add_middleware(JWTMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],            # List of allowed origins
    allow_credentials=True,           # Allow cookies / credentials
    allow_methods=["*"],              # Allow all HTTP methods
    allow_headers=["*"],              # Allow all headers
)


@app.get("/ping")
def read_root():
    return {"status": "server is up and running"}

@app.post("/login")
def login(data: LoginRequest, response: Response):
    if data.password == "" or data.email == "":
        raise HTTPException(status_code=401, detail="Invalid email or password")

    user = mongo_find_one({"email": data.email}, "users")
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not user.get("approved"):
        raise HTTPException(status_code=401, detail="User not approved")
    
    if not verify_password(data.password, user.get("password")):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
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
    del user["password"]
    return {"message": "Logged in, token set in cookie", "success": True, "data": user}

@app.post("/register")
def register(data: RegisterRequest, response: Response):
    if data.password == "" or data.email == "":
        raise HTTPException(status_code=401, detail="Invalid email or password")

    mongo_create_one({"email": data.email, "password": hash_password(data.password), "name": data.name, "plan": "free", "approved": False}, "users")
    user = mongo_find_one({"email": data.email}, "users")
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {"message": "user registered successfully, please wait for approval", "success": True, "data": user}

@app.post("/logout")
def logout(response: Response):
    response.cookies.delete("access_token")
    return {"message": "Logged out successfully", "success": True}

@app.get("/user")
def user():
    return {"message": "User is logged in", "success": True}


@app.post("/chat")
def chat(message: Message, request: Request):
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="user not logged in")
    
    job_id = str(uuid.uuid4())
    if not queue_task_helper(user.get("_id"), job_id, "process_message", message.message, message.doc_id):
        raise HTTPException(status_code=500, detail="Failed to queue document")
    
    return {"status": "success", "job_id": job_id}

@app.post("/upload")
def upload(request: Request, file: UploadFile = File(...)):
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="user not logged in")
    file.file.seek(0)
    # upload document to google drive and return file_id
    job_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".pdf", ".txt", ".docx"]:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    file_id = upload_to_gcs(file.file, job_id+ext)
    
    # queue document task
    if not queue_task_helper(user.get("_id"), job_id, "process_doc", "NA", file_id):
        raise HTTPException(status_code=500, detail="Failed to queue document")
    
    return {"status": "success", "job_id": job_id}

@app.post("/link")
def link(request: Request, message: LinkMessage):
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="user not logged in")
    
    job_id = str(uuid.uuid4())
    if not queue_task_helper(user.get("_id"), job_id, "process_link", "NA", message.message):
        raise HTTPException(status_code=500, detail="Failed to queue document")
    return {"status": "success", "job_id": job_id}

@app.get("/status/{id}")
def get_status(id: str):
    job_data = redis_queue_get_data(id)
    return {"status": "success", "job_data": job_data}