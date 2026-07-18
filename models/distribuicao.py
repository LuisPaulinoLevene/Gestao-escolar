from sqlalchemy import Column, Integer, ForeignKey, String
from database import Base


class Distribuicao(Base):

    __tablename__ = "distribuicoes"

    id = Column(Integer, primary_key=True, index=True)

    professor_id = Column(
        Integer,
        ForeignKey("professores.id")
    )

    classe_id = Column(
        Integer,
        ForeignKey("classes.id")
    )

    turma_id = Column(
        Integer,
        ForeignKey("turmas.id")
    )

    ano_letivo = Column(Integer)
