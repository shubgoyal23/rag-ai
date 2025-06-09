from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from helpers.jwt_utils import verify_token
from helpers.mongo_connect import mongo_find_one
from bson.objectid import ObjectId
INCLUDE_PATHS = ["/chat", "/user", "/upload", "/link", "/status/"]

class JWTMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        path = request.url.path
        if path not in INCLUDE_PATHS:
            return await call_next(request)

        # 1. Check cookie
        token = request.cookies.get("access_token")

        if not token:
            return JSONResponse(status_code=401, content={"detail": "user not logged in"})

        payload = verify_token(token)
        if not payload:
            return JSONResponse(status_code=401, content={"detail": "Invalid token"})
        
        user_id = payload.get("sub")
        if not user_id:
            return JSONResponse(status_code=401, content={"detail": "Invalid token"})
        
        user = mongo_find_one({"_id": ObjectId(user_id)}, "users")
        if not user:
            return JSONResponse(status_code=401, content={"detail": "Invalid token"})
        if not user.get("approved"):
            return JSONResponse(status_code=401, content={"detail": "User not approved"})
        del user["password"]
        request.state.user = user
        return await call_next(request)

