import uvicorn
import asyncio
from fastapi import FastAPI
from app.database import init_db

# Импортируем роутеры как часть пакета app
from app.routes import stack, user


app = FastAPI()
app.include_router(user.router)
app.include_router(stack.router)



if __name__ == "__main__":
    asyncio.run(init_db())
    uvicorn.run(app)