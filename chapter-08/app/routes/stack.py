from fastapi import HTTPException, APIRouter, HTTPBearer, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from models import User
import services.stack
import services.user
import utils


class PushElement(BaseModel):
    value: int


router = APIRouter(pref="/stack")
security = HTTPBearer()


# Dependency для проверки JWT токена и получения текущего пользователя
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = await utils.verify_jwt_token(token)
    username = payload.get("sub")
    
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = await services.user.get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user


# Защищенные эндпоинты (требуют JWT токен)

@router.get('/pop')
async def pop_element(current_user: User = Depends(get_current_user)):
    user_id = current_user.id
    if await services.stack.get_size(user_id) <= 0:
        raise HTTPException(status_code=404, detail="No elements in stack")
    
    value = await services.pop(user_id)
    return {"message": f"The last value is {value}"}


@router.post('/push')
async def push_element(
    input: PushElement,
    current_user: User = Depends(get_current_user)
):
    user_id = current_user.id
    await services.stack.push(user_id, input.value)
    return {"message": f"{input.value} is added"}


@router.get('/size')
async def get_stack_size(current_user: User = Depends(get_current_user)):
    user_id = current_user.id
    length = await services.stack.get_size(user_id)
    return {
        "stack_size": length,
        "is_empty": length == 0
    }


@router.delete('/clear')
async def clear_stack(current_user: User = Depends(get_current_user)):
    user_id = current_user.id
    await services.stack.delete_all(user_id)
    return {"message": "Стек очищен"}