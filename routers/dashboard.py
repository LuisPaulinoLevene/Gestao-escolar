# routers/dashboard.py
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.professor import Professor as ProfessorModel
from models.distribuicao import Distribuicao as DistribuicaoModel
from models.turma import Turma as TurmaModel
from models.classe import Classe as ClasseModel
from models.aluno import Aluno as AlunoModel
from models.matricula import Matricula as MatriculaModel
from models.escola import Escola


from database import get_db
from models.admin import Admin as AdminModel
from models.chefe_secretaria import ChefeSecretaria as ChefeSecretariaModel
from models.dap import DAP as DAPModel
from models.funcionario_secretaria import FuncionarioSecretaria as FuncionarioSecretariaModel
from models.director import Director as DirectorModel
from models.usuario_professor import UsuarioProfessor as UsuarioProfessorModel
from utils.normalizar import normalizar_username
from fastapi.templating import Jinja2Templates

# Caminho onde seus templates HTML estão salvos
templates = Jinja2Templates(directory="templates")

router = APIRouter(tags=["dashboard"])


@router.post("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    usuario: str = Form(...),
    senha: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    # Normaliza o nome
    usuario_normalizado = normalizar_username(usuario)

    # Checa em cada tabela
    result = await db.execute(select(AdminModel).where(AdminModel.nome == usuario_normalizado))
    admin = result.scalar_one_or_none()
    if admin and admin.senha == senha:
        return templates.TemplateResponse("admin.html", {"request": request})

    result = await db.execute(select(ChefeSecretariaModel).where(ChefeSecretariaModel.nome == usuario_normalizado))
    chefe = result.scalar_one_or_none()
    if chefe and chefe.senha == senha:
        return templates.TemplateResponse("chefe_secretaria.html", {"request": request})

    result = await db.execute(select(DAPModel).where(DAPModel.nome == usuario_normalizado))
    dap = result.scalar_one_or_none()
    if dap and dap.senha == senha:
        return templates.TemplateResponse("dap.html", {"request": request})

    result = await db.execute(select(FuncionarioSecretariaModel).where(FuncionarioSecretariaModel.nome == usuario_normalizado))
    funcionario = result.scalar_one_or_none()
    if funcionario and funcionario.senha == senha:
        return templates.TemplateResponse("funcionario_secretaria.html", {"request": request})

    result = await db.execute(select(DirectorModel).where(DirectorModel.nome == usuario_normalizado))
    director = result.scalar_one_or_none()
    if director and director.senha == senha:
        return templates.TemplateResponse("director.html", {"request": request})

    # ==========================================
    # LOGIN PROFESSOR
    # ==========================================

    result = await db.execute(

        select(ProfessorModel)

        .where(
            ProfessorModel.nome.ilike(usuario_normalizado)
        )

    )

    professor = result.scalar_one_or_none()

    if professor:

        result = await db.execute(

            select(UsuarioProfessorModel)

            .where(

                UsuarioProfessorModel.professor_id == professor.id

            )

        )


        usuario_prof = result.scalar_one_or_none()

        print("==============================")
        print("PROFESSOR ENCONTRADO:", professor)
        print("PROFESSOR ID:", professor.id if professor else None)
        print("USUARIO PROFESSOR:", usuario_prof)
        print("SENHA DIGITADA:", senha)
        print("SENHA BANCO:", usuario_prof.senha if usuario_prof else None)
        print("==============================")

        if usuario_prof and usuario_prof.senha == senha:

            # ===========================
            # BUSCAR PROFESSOR
            # ===========================

            result = await db.execute(
                select(ProfessorModel)
                .where(
                    ProfessorModel.id == usuario_prof.professor_id
                )
            )

            professor = result.scalar_one_or_none()

            if not professor:
                raise HTTPException(
                    status_code=404,
                    detail="Professor não encontrado"
                )

            # ===========================
            # BUSCAR DISTRIBUIÇÃO
            # ===========================

            result = await db.execute(
                select(DistribuicaoModel)
                .where(
                    DistribuicaoModel.professor_id == professor.id
                )
            )

            distribuicao = result.scalar_one_or_none()

            turma = None
            classe = None
            alunos = []

            if distribuicao:
                # Buscar turma

                result = await db.execute(
                    select(TurmaModel)
                    .where(
                        TurmaModel.id == distribuicao.turma_id
                    )
                )

                turma = result.scalar_one_or_none()

                # Buscar classe

                result = await db.execute(
                    select(ClasseModel)
                    .where(
                        ClasseModel.id == distribuicao.classe_id
                    )
                )

                classe = result.scalar_one_or_none()
                print("==============================")
                print("PROFESSOR LOGIN:", professor.nome)
                print("PROFESSOR ID:", professor.id)
                print("DISTRIBUICAO:", distribuicao)
                print("==============================")

                # Buscar alunos da turma

                # ===========================
                # Buscar alunos da turma
                # através das matrículas
                # ===========================

                result = await db.execute(
                    select(AlunoModel)
                    .join(
                        MatriculaModel,
                        MatriculaModel.aluno_id == AlunoModel.id
                    )
                    .where(
                        MatriculaModel.turma_id == distribuicao.turma_id
                    )
                )

                alunos = result.scalars().all()

                # ===========================
                # ESTATÍSTICA
                # ===========================

            homens = 0
            mulheres = 0

            for aluno in alunos:

                if aluno.sexo:

                    sexo = aluno.sexo.upper()

                    if sexo == "M" or sexo == "H":
                        homens += 1

                    elif sexo == "F":
                        mulheres += 1

            total = len(alunos)

            print("==============================")
            print("PROFESSOR:", professor.nome if professor else None)
            print("DISTRIBUICAO:", distribuicao)
            print("TURMA:", turma)
            print("CLASSE:", classe)
            print("==============================")

            result = await db.execute(
                select(Escola)
            )

            escola = result.scalar_one_or_none()

            # ===========================
            # MOSTRAR TURMA DO PROFESSOR
            # ===========================

            return templates.TemplateResponse(
                "professor_turma.html",
                {
                    "request": request,

                    "professor": professor,

                    "turma": turma,

                    "classe": classe,

                    "alunos": alunos,

                    "homens": homens,

                    "mulheres": mulheres,

                    "total": total,

                    "ano": distribuicao.ano_letivo if distribuicao else "",

                    "escola": escola
                }
            )

        # login inválido

        raise HTTPException(
            status_code=401,
            detail="Usuário ou senha inválidos"
        )