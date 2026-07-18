from pydantic import BaseModel
from datetime import date


class MatriculaCreate(BaseModel):
    aluno_id: int
    classe_id: int
    turma_id: int
    ano_letivo: int



class MatriculaResponse(BaseModel):

    id: int

    aluno_id: int
    classe_id: int
    turma_id: int

    ano_letivo: int
    status: str


    # Dados do aluno
    aluno_nome: str
    sexo: str
    data_nascimento: date


    # Dados da turma
    classe_nome: str
    turma_nome: str


    class Config:
        from_attributes = True