from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from backend import stack

pages = APIRouter(prefix="")
templates = Jinja2Templates(directory="templates")

@pages.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(
        "index.html", {"request": request, "user": "олег", "stack": stack}
    )