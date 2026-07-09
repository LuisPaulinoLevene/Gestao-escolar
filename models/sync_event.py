from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON
from sqlalchemy.sql import func

from database.primary import Base


class SyncEvent(Base):

    __tablename__ = "sync_events"


    id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    tabela = Column(
        String(100),
        nullable=False
    )


    registro_id = Column(
        String(100),
        nullable=False
    )


    operacao = Column(
        String(20),
        nullable=False
    )


    dados = Column(
        JSON,
        nullable=True
    )

    banco_origem = Column(
        String(20),
        nullable=False,
        default="PRIMARY"
    )


    sincronizado = Column(
        Boolean,
        default=False
    )


    criado_em = Column(
        DateTime,
        server_default=func.now()
    )