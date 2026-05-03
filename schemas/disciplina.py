from pydantic import BaseModel
from typing import Optional

class DisciplinaBase(BaseModel):
    disciplina: str
    classe_id: int
    turma_id: Optional[int] = None
    is_personalizada: bool = False


class DisciplinaCreate(DisciplinaBase):
    pass


class DisciplinaResponse(DisciplinaBase):
    id: int

    class Config:
        from_attributes = True