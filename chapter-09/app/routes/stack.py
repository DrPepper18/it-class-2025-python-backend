from fastapi import HTTPException, APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from app.models import User
from app.services import stack
from app.services import user as user_service
from app.utils import verify_jwt_token


class PushElement(BaseModel):
    value: int


router = APIRouter(prefix="/stack")
security = HTTPBearer()


# Dependency для проверки JWT токена и получения текущего пользователя
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = verify_jwt_token(token)
    username = payload.get("sub")
    
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = await user_service.get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user


# Защищенные эндпоинты (требуют JWT токен)

@router.get('/pop')
async def pop_element(current_user: User = Depends(get_current_user)):
    user_id = current_user.id
    if await stack.get_size(user_id) <= 0:
        raise HTTPException(status_code=404, detail="No elements in stack")
    
    value = await stack.pop(user_id)
    return {"message": f"The last value is {value}"}


@router.post('/push')
async def push_element(
    input: PushElement,
    current_user: User = Depends(get_current_user)
):
    user_id = current_user.id
    await stack.push(user_id, input.value)
    return {"message": f"{input.value} is added"}


@router.get('/size')
async def get_stack_size(current_user: User = Depends(get_current_user)):
    user_id = current_user.id
    length = await stack.get_size(user_id)
    return {
        "stack_size": length,
        "is_empty": length == 0
    }


@router.delete('/clear')
async def clear_stack(current_user: User = Depends(get_current_user)):
    user_id = current_user.id
    await stack.delete_all(user_id)
    return {"message": "Стек очищен"}