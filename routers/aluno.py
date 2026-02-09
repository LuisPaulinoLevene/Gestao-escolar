from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from database import get_db
from models.aluno import Aluno as AlunoModel
from schemas.aluno import AlunoCreate, Aluno

router = APIRouter(prefix="/alunos", tags=["Alunos"])


# Criar aluno
@router.post("/", response_model=Aluno)
async def create_aluno(aluno: AlunoCreate, db: AsyncSession = Depends(get_db)):
    db_aluno = AlunoModel(
        nome=aluno.nome,
        data_nascimento=aluno.data_nascimento,
        sexo=aluno.sexo
    )
    db.add(db_aluno)
    await db.commit()
    await db.refresh(db_aluno)
    return db_aluno


# Listar todos alunos
@router.get("/", response_model=List[Aluno])
async def get_alunos(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AlunoModel))
    return result.scalars().all()


# Buscar aluno por id
@router.get("/{aluno_id}", response_model=Aluno)
async def get_aluno(aluno_id: int = Path(..., gt=0), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AlunoModel).where(AlunoModel.id == aluno_id))
    aluno = result.scalar_one_or_none()
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    return aluno


# Atualizar aluno
@router.put("/{aluno_id}", response_model=Aluno)
async def update_aluno(aluno_id: int, aluno_update: AlunoCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AlunoModel).where(AlunoModel.id == aluno_id))
    aluno = result.scalar_one_or_none()
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")

    aluno.nome = aluno_update.nome
    aluno.data_nascimento = aluno_update.data_nascimento
    aluno.sexo = aluno_update.sexo

    db.add(aluno)
    await db.commit()
    await db.refresh(aluno)
    return aluno


# Apagar aluno
@router.delete("/{aluno_id}", response_model=dict)
async def delete_aluno(aluno_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AlunoModel).where(AlunoModel.id == aluno_id))
    aluno = result.scalar_one_or_none()
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")

    await db.delete(aluno)
    await db.commit()
    return {"message": f"Aluno {aluno_id} removido com sucesso"}
