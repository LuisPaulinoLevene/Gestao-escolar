from pydantic import BaseModel

class UsuarioProfessorCreate(BaseModel):

    professor_id: int

    senha: str


class UsuarioProfessorResponse(BaseModel):

    id: int

    professor_id: int

    nome: str

    senha: str

    class Config:
        from_attributes = True