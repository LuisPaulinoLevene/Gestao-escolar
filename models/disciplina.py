from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from database import Base

class Disciplina(Base):
    __tablename__ = "disciplinas"

    id = Column(Integer, primary_key=True, index=True)

    disciplina = Column(String(100), nullable=False)

    # disciplina base da classe
    classe_id = Column(Integer, ForeignKey("classes.id"), nullable=False)

    # opcional: disciplina específica de uma turma
    turma_id = Column(Integer, ForeignKey("turmas.id"), nullable=True)

    # marca se é override de turma
    is_personalizada = Column(Boolean, default=False)