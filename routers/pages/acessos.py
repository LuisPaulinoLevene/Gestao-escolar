from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/acessos", response_class=HTMLResponse)
async def acessos(request: Request):
    return templates.TemplateResponse(
        "acessos_professor.html",
        {"request": request}
    )