from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from database import get_db
from models.assistencia import AssistenciaMutua
from models.contacto_professor import ContactoProfessor
from schemas.assistencia import AssistenciaCreate, AssistenciaResponse
from typing import List

router = APIRouter(prefix="/assistencias", tags=["Assistências Mútuas"])


# 🔹 Listar Professores (para dropdown)
@router.get("/professores")
async def listar_professores(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ContactoProfessor))
    professores = result.scalars().all()

    return [
        {"id": p.id, "nome": p.nome}
        for p in professores
    ]


# 🔹 Criar Assistência
@router.post("/", response_model=AssistenciaResponse)
async def criar_assistencia(
    dados: AssistenciaCreate,
    db: AsyncSession = Depends(get_db)
):

    nova = AssistenciaMutua(**dados.dict())
    db.add(nova)
    await db.commit()
    await db.refresh(nova)

    # Buscar nomes
    assistido = await db.get(ContactoProfessor, dados.professor_assistido_id)
    assistente = await db.get(ContactoProfessor, dados.professor_assistente_id)

    return {
        "id": nova.id,
        "disciplina": nova.disciplina,
        "data_hora": nova.data_hora,
        "criado_em": nova.criado_em,
        "professor_assistido_nome": assistido.nome,
        "professor_assistente_nome": assistente.nome
    }


# 🔹 Listar
@router.get("/", response_model=List[AssistenciaResponse])
async def listar_assistencias(db: AsyncSession = Depends(get_db)):

    result = await db.execute(
        select(AssistenciaMutua)
        .options(selectinload(AssistenciaMutua.professor_assistido))
        .options(selectinload(AssistenciaMutua.professor_assistente))
    )

    assistencias = result.scalars().all()

    return [
        {
            "id": a.id,
            "disciplina": a.disciplina,
            "data_hora": a.data_hora,
            "criado_em": a.criado_em,
            "professor_assistido_nome": a.professor_assistido.nome,
            "professor_assistente_nome": a.professor_assistente.nome
        }
        for a in assistencias
    ]


# 🔹 Atualizar
@router.put("/{assistencia_id}")
async def atualizar_assistencia(
    assistencia_id: int,
    dados: AssistenciaCreate,
    db: AsyncSession = Depends(get_db)
):
    assistencia = await db.get(AssistenciaMutua, assistencia_id)

    if not assistencia:
        raise HTTPException(status_code=404, detail="Assistência não encontrada")

    for key, value in dados.dict().items():
        setattr(assistencia, key, value)

    await db.commit()
    return {"message": "Atualizado com sucesso"}


# 🔹 Apagar
@router.delete("/{assistencia_id}")
async def apagar_assistencia(
    assistencia_id: int,
    db: AsyncSession = Depends(get_db)
):
    assistencia = await db.get(AssistenciaMutua, assistencia_id)

    if not assistencia:
        raise HTTPException(status_code=404, detail="Assistência não encontrada")

    await db.delete(assistencia)
    await db.commit()

    return {"message": "Removido com sucesso"}
