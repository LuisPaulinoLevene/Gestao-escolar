from pydantic import BaseModel


class EscolaBase(BaseModel):
    provincia: str
    distrito: str
    nome: str


class EscolaCreate(EscolaBase):
    pass


class EscolaUpdate(EscolaBase):
    pass


class EscolaResponse(EscolaBase):
    id: int

    class Config:
        from_attributes = True