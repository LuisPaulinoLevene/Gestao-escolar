from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from database import Base


class SMSLog(Base):
    __tablename__ = "sms_logs"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(String, nullable=False)
    mensagem = Column(Text, nullable=False)
    numeros = Column(Text, nullable=False)  # lista convertida para string
    status = Column(String, nullable=False)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
