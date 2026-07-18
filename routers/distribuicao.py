from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from sqlalchemy import select

from models.distribuicao import Distribuicao as DistribuicaoModel
from schemas.distribuicao import DistribuicaoCreate, Distribuicao


router = APIRouter(
    prefix="/distribuicoes",
    tags=["Distribuição"]
)



@router.post("/", response_model=Distribuicao)
async def criar_distribuicao(
    dados:DistribuicaoCreate,
    db:AsyncSession=Depends(get_db)
):

    distribuicao = DistribuicaoModel(
        professor_id=dados.professor_id,
        classe_id=dados.classe_id,
        turma_id=dados.turma_id,
        ano_letivo=dados.ano_letivo
    )


    db.add(distribuicao)

    await db.commit()

    await db.refresh(distribuicao)

    return distribuicao

@router.get("/verificar/")
async def verificar_distribuicao(
    classe_id:int,
    turma_id:int,
    ano_letivo:int,
    db:AsyncSession=Depends(get_db)
):

    resultado = await db.execute(

        select(DistribuicaoModel)

        .where(

            DistribuicaoModel.classe_id == classe_id,

            DistribuicaoModel.turma_id == turma_id,

            DistribuicaoModel.ano_letivo == ano_letivo

        )

    )


    distribuicao = resultado.scalars().first()



    if not distribuicao:

        return {
            "existe":False
        }



    return {

        "existe":True,

        "id":distribuicao.id,

        "professor_id":distribuicao.professor_id

    }

@router.put("/{id}")
async def atualizar_distribuicao(

    id:int,

    dados:DistribuicaoCreate,

    db:AsyncSession=Depends(get_db)

):


    resultado = await db.execute(

        select(DistribuicaoModel)

        .where(
            DistribuicaoModel.id==id
        )

    )


    distribuicao = resultado.scalars().first()



    if not distribuicao:

        raise HTTPException(
            status_code=404,
            detail="Distribuição não encontrada"
        )



    distribuicao.professor_id = dados.professor_id



    await db.commit()

    await db.refresh(distribuicao)



    return distribuicao