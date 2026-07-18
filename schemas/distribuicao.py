from pydantic import BaseModel


class DistribuicaoCreate(BaseModel):

    professor_id:int
    classe_id:int
    turma_id:int
    ano_letivo:int



class Distribuicao(BaseModel):

    id:int
    professor_id:int
    classe_id:int
    turma_id:int
    ano_letivo:int

    class Config:
        from_attributes=True