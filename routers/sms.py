from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from schemas.sms import SMSRequest, SMSResponse
from models.sms import SMSLog
import httpx
import json

router = APIRouter(prefix="/sms", tags=["SMS"])

# 🔐 SEU TOKEN (como solicitado)
MOZESMS_TOKEN = "bWtfZWI2ZjdiZDRmNTE4OWMyM2U0MTQ1NGQ4YjE0NzgxYjk6MTM2OnNrX2IxMzZlMmEyOWY1ZmI3MzkzYWE1OTU1YmM4MDFhZjE1YzQ1MDE4MGIyMTJkNzdiNTcwMzhiYzRjMjRmMzA2NTA="

MOZESMS_URL = "https://api.mozesms.com/v1/sms/bulk"


@router.post("/enviar", response_model=SMSResponse)
async def enviar_sms(
    dados: SMSRequest,
    db: AsyncSession = Depends(get_db)
):

    headers = {
        "Authorization": f"Bearer {MOZESMS_TOKEN}",
        "Content-Type": "application/json"
    }

    mensagens = [
        {"to": numero, "text": dados.mensagem}
        for numero in dados.numeros
    ]

    payload = {
        "from": dados.sender_id,
        "messages": mensagens
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                MOZESMS_URL,
                headers=headers,
                json=payload
            )

        resposta_api = response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text

        # 🔥 Salvar log no banco
        novo_log = SMSLog(
            sender_id=dados.sender_id,
            mensagem=dados.mensagem,
            numeros=json.dumps(dados.numeros),
            status=str(response.status_code)
        )

        db.add(novo_log)
        await db.commit()

        return {
            "status_code": response.status_code,
            "resposta": resposta_api
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao enviar SMS: {str(e)}"
        )
