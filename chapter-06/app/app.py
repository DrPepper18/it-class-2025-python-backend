import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import services


app = FastAPI()

class PushElement(BaseModel):
    value: int


@app.get('/pop')
async def pop_element():
    if await services.get_size() <= 0:
        raise HTTPException(status_code=404, detail="No elements in stack")
    
    return {"message": f"The last value is {await services.pop()}"}

@app.post('/push')
async def push_element(input: PushElement):
    await services.push(input.value)
    return {"message": f"{input.value} is added"}

@app.get('/size')
async def get_stack_size():
    length = await services.get_size()
    return {
        "stack_size": length,
        "is_empty": length == 0
    }

@app.delete('/clear')
async def clear_stack():
    await services.delete_all()
    return {"message": "Стек очищен"}

if __name__ == "__main__":
    uvicorn.run(app)