import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


app = FastAPI()

stack = list()

class PushElement(BaseModel):
    value: int


@app.get('/pop')
def pop_element():
    if not stack:
        raise HTTPException(status_code=404, detail="No elements in stack")
    
    return {"message": f"The last value is {stack.pop()}"}

@app.post('/push')
def push_element(input: PushElement):
    stack.append(input.value)
    return {"message": f"{input.value} is added"}

@app.get('/size')
def get_stack_size():
    return {
        "stack_size": len(stack),
        "is_empty": len(stack) == 0
    }

@app.delete('/clear')
def clear_stack():
    stack.clear()
    return {"message": "Стек очищен"}

if __name__ == "__main__":
    uvicorn.run(app)