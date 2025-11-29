from fastapi import HTTPException, APIRouter
from pydantic import BaseModel
import services.user
import utils


class RegisterRequest(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


router = APIRouter(prefix="/users")

# Эндпоинт регистрации
@router.post('/register')
async def register(request: RegisterRequest):
    user = await services.user.register_user(request.username, request.password)
    
    if not user:
        raise HTTPException(
            status_code=400, 
            detail="Username already exists"
        )
    
    return {
        "message": "User registered successfully",
        "username": user.username
    }


# Эндпоинт входа
@router.post('/login')
async def login(request: LoginRequest):
    user = await services.user.login_user(request.username, request.password)
    
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )
    
    # Создаем JWT токен
    token = await utils.create_jwt_token(user.username)
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "username": user.username
    }