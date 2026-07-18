from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.classe import Classe

from database import get_db

from models.professor import Professor
from models.turma import Turma
from models.aluno import Aluno
from models.distribuicao import Distribuicao
from models.matricula import Matricula


router = APIRouter()

templates = Jinja2Templates(directory="templates")



@router.get("/usuario_professor", response_class=HTMLResponse)
async def usuario_professor(
    request: Request,
    db: AsyncSession = Depends(get_db)
):


    # ======================================
    # PROFESSOR LOGADO
    # TEMPORÁRIO
    # depois será substituído pela sessão
    # ======================================

    professor_id = 1



    # ======================================
    # BUSCAR PROFESSOR
    # ======================================

    result = await db.execute(

        select(Professor)

        .where(
            Professor.id == professor_id
        )

    )

    professor = result.scalar_one_or_none()



    if not professor:

        return templates.TemplateResponse(
            "professor_turma.html",
            {
                "request":request,

                "professor":None,

                "turma":None,

                "alunos":[],

                "homens":0,

                "mulheres":0,

                "total":0
            }
        )



    # ======================================
    # BUSCAR DISTRIBUIÇÃO DO PROFESSOR
    # ======================================


    result = await db.execute(

        select(Distribuicao)

        .where(
            Distribuicao.professor_id == professor_id
        )

    )


    distribuicao = result.scalar_one_or_none()

    turma = None
    classe = None
    alunos = []



    # ======================================
    # BUSCAR TURMA ATRIBUÍDA
    # ======================================

    if distribuicao:
        result = await db.execute(

            select(Turma)

            .where(
                Turma.id == distribuicao.turma_id
            )

        )

        turma = result.scalar_one_or_none()

        # BUSCAR CLASSE

        result = await db.execute(

            select(Classe)

            .where(
                Classe.id == distribuicao.classe_id
            )

        )

        classe = result.scalar_one_or_none()




    # ======================================
    # BUSCAR ALUNOS DA TURMA
    # ATRAVÉS DA MATRÍCULA
    # ======================================


    if turma:


        result = await db.execute(

            select(Aluno)

            .join(
                Matricula,
                Matricula.aluno_id == Aluno.id
            )

            .where(

                Matricula.turma_id == turma.id

            )

        )


        alunos = result.scalars().all()



    # ======================================
    # ESTATÍSTICA
    # ======================================


    homens = 0

    mulheres = 0



    for aluno in alunos:


        if aluno.sexo:


            sexo = aluno.sexo.upper()


            if sexo == "M":

                homens += 1


            elif sexo == "F":

                mulheres += 1




    total = len(alunos)




    # ======================================
    # ENVIAR PARA HTML
    # ======================================


    return templates.TemplateResponse(

        "professor_turma.html",

        {

            "request":request,

            "professor":professor,

            "classe": classe,

            "turma":turma,

            "alunos":alunos,

            "homens":homens,

            "mulheres":mulheres,

            "total":total,

            "ano": distribuicao.ano_letivo if distribuicao else ""


        }

    )