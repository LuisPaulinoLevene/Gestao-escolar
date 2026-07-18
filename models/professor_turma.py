from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base


class ProfessorTurma(Base):

    __tablename__ = "professor_turmas"


    id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    professor_id = Column(
        Integer,
        ForeignKey("professores.id"),
        nullable=False
    )


    turma_id = Column(
        Integer,
        ForeignKey("turmas.id"),
        nullable=False
    )


    carga_horaria = Column(
        Integer,
        nullable=False
    )


    ano_letivo = Column(
        String,
        nullable=False
    )