from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


router = APIRouter()


templates = Jinja2Templates(directory="templates")



@router.get("/alunos_por_turma", response_class=HTMLResponse)
async def alunos_por_turma(request: Request):

    return templates.TemplateResponse(
        "alunos_por_turma.html",
        {
            "request":request
        }
    )