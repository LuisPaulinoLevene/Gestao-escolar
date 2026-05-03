from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_
from typing import List

from database import get_db
from models.disciplina import Disciplina
from models.classe import Classe
from models.turma import Turma
from schemas.disciplina import DisciplinaCreate, DisciplinaResponse

router = APIRouter(
    prefix="/disciplinas",
    tags=["Disciplinas"]
)

# ===================== CRIAR =====================
@router.post("/", response_model=DisciplinaResponse)
async def criar_disciplina(
    dados: DisciplinaCreate,
    db: AsyncSession = Depends(get_db)
):

    # validar classe
    classe = await db.execute(
        select(Classe).where(Classe.id == dados.classe_id)
    )
    if not classe.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Classe não encontrada")

    # validar turma (se existir)
    if dados.turma_id:
        turma = await db.execute(
            select(Turma).where(Turma.id == dados.turma_id)
        )
        if not turma.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Turma não encontrada")

    # evitar duplicação exata
    result = await db.execute(
        select(Disciplina).where(
            Disciplina.disciplina == dados.disciplina,
            Disciplina.classe_id == dados.classe_id,
            Disciplina.turma_id == dados.turma_id
        )
    )

    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Disciplina já existe nesse contexto")

    nova = Disciplina(
        disciplina=dados.disciplina,
        classe_id=dados.classe_id,
        turma_id=dados.turma_id,
        is_personalizada=dados.is_personalizada
    )

    db.add(nova)
    await db.commit()
    await db.refresh(nova)

    return nova


# ===================== LISTAR TODAS =====================
@router.get("/", response_model=List[DisciplinaResponse])
async def listar_disciplinas(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Disciplina))
    return result.scalars().all()


# ===================== DISCIPLINAS DE UMA TURMA =====================
@router.get("/turma/{turma_id}", response_model=List[DisciplinaResponse])
async def disciplinas_por_turma(turma_id: int, db: AsyncSession = Depends(get_db)):

    # 1. tentar disciplinas específicas da turma
    result = await db.execute(
        select(Disciplina).where(Disciplina.turma_id == turma_id)
    )
    turmas = result.scalars().all()

    if turmas:
        return turmas

    # 2. fallback → usar classe da turma
    turma = await db.execute(
        select(Turma).where(Turma.id == turma_id)
    )
    turma_obj = turma.scalar_one_or_none()

    if not turma_obj:
        raise HTTPException(status_code=404, detail="Turma não encontrada")

    result = await db.execute(
        select(Disciplina).where(
            Disciplina.classe_id == turma_obj.classe_id
        )
    )

    return result.scalars().all()


# ===================== BUSCAR =====================
@router.get("/{disciplina_id}", response_model=DisciplinaResponse)
async def buscar_disciplina(disciplina_id: int, db: AsyncSession = Depends(get_db)):

    result = await db.execute(
        select(Disciplina).where(Disciplina.id == disciplina_id)
    )

    disciplina = result.scalar_one_or_none()

    if not disciplina:
        raise HTTPException(status_code=404, detail="Disciplina não encontrada")

    return disciplina


# ===================== ATUALIZAR =====================
@router.put("/{disciplina_id}", response_model=DisciplinaResponse)
async def atualizar_disciplina(
    disciplina_id: int,
    dados: DisciplinaCreate,
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(Disciplina).where(Disciplina.id == disciplina_id)
    )

    disciplina = result.scalar_one_or_none()

    if not disciplina:
        raise HTTPException(status_code=404, detail="Disciplina não encontrada")

    disciplina.disciplina = dados.disciplina
    disciplina.classe_id = dados.classe_id
    disciplina.turma_id = dados.turma_id
    disciplina.is_personalizada = dados.is_personalizada

    await db.commit()
    await db.refresh(disciplina)

    return disciplina


# =================== APAGAR =================
@router.delete("/{disciplina_id}")
async def apagar_disciplina(disciplina_id: int, db: AsyncSession = Depends(get_db)):

    result = await db.execute(
        select(Disciplina).where(Disciplina.id == disciplina_id)
    )

    disciplina = result.scalar_one_or_none()

    if not disciplina:
        raise HTTPException(status_code=404, detail="Disciplina não encontrada")

    await db.delete(disciplina)
    await db.commit()

    return {"message": "Removida com sucesso"}