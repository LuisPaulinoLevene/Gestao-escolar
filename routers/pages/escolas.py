from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/escolas", response_class=HTMLResponse)
async def escolas(request: Request):
    return templates.TemplateResponse(
        "escolas.html",
        {"request": request}
    )