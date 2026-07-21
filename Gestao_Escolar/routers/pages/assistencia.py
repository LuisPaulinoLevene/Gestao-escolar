from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/assistencias", response_class=HTMLResponse)
async def assistencias(request: Request):
    return templates.TemplateResponse(
        "assistencias.html",
        {"request": request}
    )
