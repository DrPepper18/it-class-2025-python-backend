from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

pages = APIRouter(prefix="")

# Настраиваем шаблонизатор
templates = Jinja2Templates(directory="templates")

# Главная страница
@pages.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(
        "index.html", {"request": request, "user": None}
    )