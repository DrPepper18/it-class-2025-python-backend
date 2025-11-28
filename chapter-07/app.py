import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend import services
from frontend import pages

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(services)
app.include_router(pages)


if __name__ == "__main__":
    uvicorn.run(app)