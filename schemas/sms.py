from pydantic import BaseModel
from typing import List


class SMSRequest(BaseModel):
    sender_id: str
    mensagem: str
    numeros: List[str]


class SMSResponse(BaseModel):
    status_code: int
    resposta: dict | str
