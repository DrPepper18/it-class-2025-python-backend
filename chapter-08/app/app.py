import uvicorn
from fastapi import FastAPI
from routes import stack, user


app = FastAPI()
app.include_router(user.router)
app.include_router(stack.router)


if __name__ == "__main__":
    uvicorn.run(app)