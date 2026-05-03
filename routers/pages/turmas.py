from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/turmas", response_class=HTMLResponse)
async def turmas(request: Request):
    return templates.TemplateResponse(
        "turmas.html",
        {"request": request}
    )