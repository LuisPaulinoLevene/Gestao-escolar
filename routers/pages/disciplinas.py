from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/disciplinas", response_class=HTMLResponse)
async def disciplinas(request: Request):
    return templates.TemplateResponse(
        "disciplinas.html",
        {"request": request}
    )