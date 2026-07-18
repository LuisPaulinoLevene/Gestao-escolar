from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from database import get_db

from models.usuario_professor import UsuarioProfessor as UsuarioProfessorModel
from models.professor import Professor as ProfessorModel

from schemas.usuario_professor import (
    UsuarioProfessorCreate,
    UsuarioProfessorResponse
)

router = APIRouter(
    prefix="/usuarios-professores",
    tags=["Usuários Professores"]
)


# =====================================
# CRIAR USUÁRIO PROFESSOR
# =====================================
@router.post("/", response_model=UsuarioProfessorResponse)
async def create_usuario_professor(
    usuario: UsuarioProfessorCreate,
    db: AsyncSession = Depends(get_db)
):

    # verifica se professor existe
    result = await db.execute(
        select(ProfessorModel).where(
            ProfessorModel.id == usuario.professor_id
        )
    )

    professor = result.scalar_one_or_none()

    if not professor:
        raise HTTPException(
            status_code=404,
            detail="Professor não encontrado"
        )


    # verifica se já possui utilizador
    result = await db.execute(
        select(UsuarioProfessorModel).where(
            UsuarioProfessorModel.professor_id == usuario.professor_id
        )
    )

    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="Este professor já possui utilizador."
        )


    novo = UsuarioProfessorModel(

        professor_id=usuario.professor_id,

        senha=usuario.senha

    )

    db.add(novo)

    await db.commit()

    await db.refresh(novo)

    return UsuarioProfessorResponse(

        id=novo.id,

        professor_id=professor.id,

        nome=professor.nome,

        senha=novo.senha

    )


# =====================================
# LISTAR TODOS
# =====================================
@router.get("/", response_model=List[UsuarioProfessorResponse])
async def listar_usuarios_professores(
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(

        select(
            UsuarioProfessorModel,
            ProfessorModel
        )

        .join(
            ProfessorModel,
            UsuarioProfessorModel.professor_id == ProfessorModel.id
        )

    )

    lista = []

    for usuario, professor in result.all():

        lista.append(

            UsuarioProfessorResponse(

                id=usuario.id,

                professor_id=professor.id,

                nome=professor.nome,

                senha=usuario.senha

            )

        )

    return lista


# =====================================
# BUSCAR POR ID
# =====================================
@router.get("/{usuario_id}", response_model=UsuarioProfessorResponse)
async def get_usuario_professor(
    usuario_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(

        select(
            UsuarioProfessorModel,
            ProfessorModel
        )

        .join(
            ProfessorModel,
            UsuarioProfessorModel.professor_id == ProfessorModel.id
        )

        .where(
            UsuarioProfessorModel.id == usuario_id
        )

    )

    dados = result.first()

    if not dados:

        raise HTTPException(
            status_code=404,
            detail="Utilizador não encontrado"
        )

    usuario, professor = dados

    return UsuarioProfessorResponse(

        id=usuario.id,

        professor_id=professor.id,

        nome=professor.nome,

        senha=usuario.senha

    )


# =====================================
# ATUALIZAR SENHA
# =====================================
@router.put("/{usuario_id}", response_model=UsuarioProfessorResponse)
async def update_usuario_professor(
    usuario_id: int,
    usuario_update: UsuarioProfessorCreate,
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(

        select(UsuarioProfessorModel)

        .where(
            UsuarioProfessorModel.id == usuario_id
        )

    )

    usuario = result.scalar_one_or_none()

    if not usuario:

        raise HTTPException(
            status_code=404,
            detail="Utilizador não encontrado"
        )


    usuario.professor_id = usuario_update.professor_id
    usuario.senha = usuario_update.senha

    await db.commit()

    await db.refresh(usuario)


    result = await db.execute(

        select(ProfessorModel)

        .where(
            ProfessorModel.id == usuario.professor_id
        )

    )

    professor = result.scalar_one()

    return UsuarioProfessorResponse(

        id=usuario.id,

        professor_id=professor.id,

        nome=professor.nome,

        senha=usuario.senha

    )


# =====================================
# APAGAR
# =====================================
@router.delete("/{usuario_id}")
async def delete_usuario_professor(
    usuario_id: int,
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(

        select(UsuarioProfessorModel)

        .where(
            UsuarioProfessorModel.id == usuario_id
        )

    )

    usuario = result.scalar_one_or_none()

    if not usuario:

        raise HTTPException(
            status_code=404,
            detail="Utilizador não encontrado"
        )

    await db.delete(usuario)

    await db.commit()

    return {
        "message": "Utilizador removido com sucesso."
    }