from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


router = APIRouter()

templates = Jinja2Templates(directory="templates")


# ==========================
# PÁGINA DE MATRÍCULAS
# ==========================
@router.get("/matriculas", response_class=HTMLResponse)
async def pagina_matriculas(request: Request):

    return templates.TemplateResponse(
        "matricula.html",
        {
            "request": request
        }
    )