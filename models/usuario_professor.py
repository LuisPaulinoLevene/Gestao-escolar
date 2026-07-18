from sqlalchemy import Column,Integer,String,ForeignKey
from database import Base


class UsuarioProfessor(Base):

    __tablename__="usuarios_professores"

    id=Column(Integer,primary_key=True,index=True)

    professor_id=Column(
        Integer,
        ForeignKey("professores.id"),
        unique=True
    )

    senha=Column(String(255))