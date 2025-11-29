from fastapi import HTTPException, APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/services")

stack = list()

class PushElement(BaseModel):
    value: int


@router.get('/pop')
async def pop_element():
    if not stack:
        raise HTTPException(status_code=404, detail="No elements in stack")
    
    return {"message": f"The last value is {stack.pop()}"}

@router.post('/push')
async def push_element(input: PushElement):
    stack.append(input.value)
    return {"message": f"{input.value} is added"}

@router.get('/size')
async def get_stack_size():
    return {
        "stack_size": len(stack),
        "is_empty": len(stack) == 0
    }

@router.delete('/clear')
def clear_stack():
    stack.clear()
    return {"message": "Стек очищен"}