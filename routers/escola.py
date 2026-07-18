from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database import get_db
from models.escola import Escola
from schemas.escola import (
    EscolaCreate,
    EscolaUpdate,
    EscolaResponse
)

router = APIRouter(
    prefix="/escolas",
    tags=["Escola"]
)


# ===========================
# LISTAR
# ===========================

@router.get("/", response_model=list[EscolaResponse])
async def listar_escolas(
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Escola))
    return result.scalars().all()


# ===========================
# BUSCAR POR ID
# ===========================

@router.get("/{escola_id}", response_model=EscolaResponse)
async def buscar_escola(
    escola_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Escola)
        .where(Escola.id == escola_id)
    )

    escola = result.scalar_one_or_none()

    if not escola:
        raise HTTPException(
            status_code=404,
            detail="Escola não encontrada."
        )

    return escola


# ===========================
# CADASTRAR
# ===========================

@router.post("/", response_model=EscolaResponse)
async def criar_escola(
    dados: EscolaCreate,
    db: AsyncSession = Depends(get_db)
):
    escola = Escola(**dados.model_dump())

    db.add(escola)

    await db.commit()

    await db.refresh(escola)

    return escola


# ===========================
# ATUALIZAR
# ===========================

@router.put("/{escola_id}", response_model=EscolaResponse)
async def atualizar_escola(
    escola_id: int,
    dados: EscolaUpdate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Escola)
        .where(Escola.id == escola_id)
    )

    escola = result.scalar_one_or_none()

    if not escola:
        raise HTTPException(
            status_code=404,
            detail="Escola não encontrada."
        )

    for campo, valor in dados.model_dump().items():
        setattr(escola, campo, valor)

    await db.commit()

    await db.refresh(escola)

    return escola


# ===========================
# APAGAR
# ===========================

@router.delete("/{escola_id}")
async def apagar_escola(
    escola_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Escola)
        .where(Escola.id == escola_id)
    )

    escola = result.scalar_one_or_none()

    if not escola:
        raise HTTPException(
            status_code=404,
            detail="Escola não encontrada."
        )

    await db.delete(escola)

    await db.commit()

    return {
        "mensagem": "Escola removida com sucesso."
    }