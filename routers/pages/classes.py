from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/classes", response_class=HTMLResponse)
async def classes(request: Request):
    return templates.TemplateResponse(
        "classes.html",
        {"request": request}
    )