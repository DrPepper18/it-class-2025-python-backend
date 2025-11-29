import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from routes import backend
from routes import frontend

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(backend.router)
app.include_router(frontend.router)


if __name__ == "__main__":
    uvicorn.run(app)