from sqlalchemy import Column, Integer, String
from database import Base

class Escola(Base):
    __tablename__ = "escolas"

    id = Column(Integer, primary_key=True, index=True)

    provincia = Column(String(100), nullable=False)

    distrito = Column(String(100), nullable=False)

    nome = Column(String(200), nullable=False)