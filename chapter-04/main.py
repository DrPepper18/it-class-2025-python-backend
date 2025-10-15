import uvicorn
from fastapi import FastAPI

app = FastAPI()

stack = list()

@app.get('/get_request')
def get_request():
    return {"message": f"The last value is {stack.pop()}"}

@app.post('/post_request')
def post_request(input: int):
    stack.append(input)
    return {"message": f"{input} is added"}

if __name__ == "__main__":
    uvicorn.run(app)