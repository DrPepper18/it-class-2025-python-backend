from fastapi import HTTPException, APIRouter
from pydantic import BaseModel
from app.services import user as user_service
from app.utils import create_jwt_token


class RegisterRequest(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


router = APIRouter(prefix="/users")


@router.post("/register")
async def register(request: RegisterRequest):
    user = await user_service.register_user(request.username, request.password)

    if not user:
        raise HTTPException(status_code=400, detail="Username already exists")

    return {"message": "User registered successfully", "username": user.username}


@router.post("/login")
async def login(request: LoginRequest):
    user = await user_service.login_user(request.username, request.password)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # create_jwt_token — синхронная, без await
    token = create_jwt_token(user.username)

    return {"access_token": token, "token_type": "bearer", "username": user.username}
