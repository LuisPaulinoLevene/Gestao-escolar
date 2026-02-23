import asyncio
from datetime import datetime, timedelta
import httpx
from sqlalchemy import select, update
from database import SessionLocal
from models.encontro import Encontro
from routers.contactos import tipo_tabela
import os

# Intervalo de verificação do loop (em segundos)
INTERVALO_VERIFICACAO = 30

# ==========================
# Envio de SMS usando seu endpoint
# ==========================
async def enviar_sms_api(mensagem, numeros):
    """
    Envia SMS usando seu endpoint /sms/enviar
    Funciona localmente e na nuvem (Render)
    """
    base_url = os.getenv("RENDER_EXTERNAL_URL")
    if not base_url:
        base_url = "http://127.0.0.1:8000"

    url = f"{base_url}/sms/enviar"

    payload = {
        "sender_id": "PHANDIRA-2",
        "mensagem": mensagem,
        "numeros": numeros
    }

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(url, json=payload)
            if resp.status_code != 200:
                print(f"⚠️ Erro ao enviar SMS: {resp.text}")
        except Exception as e:
            print(f"⚠️ Exception ao enviar SMS: {e}")

# ==========================
# Pegar números da tabela de contactos
# ==========================
async def pegar_numeros(tipo):
    """
    Retorna lista de números de telefone por tipo:
    diretor, adjunto, professores, funcionarios, direcao
    """
    if tipo not in tipo_tabela:
        return []

    Model = tipo_tabela[tipo]
    async with SessionLocal() as db:
        result = await db.execute(select(Model))
        contactos = result.scalars().all()
        return [c.telefone for c in contactos]

# ==========================
# Monitor automático
# ==========================
async def monitorar_encontros():
    print("🔄 Monitor automático de encontros iniciado")

    while True:
        agora = datetime.now()

        async with SessionLocal() as db:
            result = await db.execute(
                select(Encontro).where(Encontro.status == "APROVADO")
            )
            encontros = result.scalars().all()

            for encontro in encontros:

                # ==========================
                # 🔔 ALERTA DIREÇÃO (2 dias antes)
                # ==========================
                momento_alerta = encontro.data_hora - timedelta(days=2)
                if encontro.alerta_enviado == "NAO" and agora >= momento_alerta:
                    # Numeros de alerta
                    if encontro.tipo == "PROFESSORES":
                        diretores = await pegar_numeros("diretor")  # Para professores, pegamos os diretores
                        numeros_alerta = diretores
                    elif encontro.tipo == "FUNCIONARIOS":
                        numeros_alerta = await pegar_numeros("direcao")  # Para funcionários, pegamos a direção
                    else:
                        continue  # ignora tipo desconhecido

                    mensagem_alerta = (
                        f"Saudacoes, ha um encontro referente a {encontro.titulo}, agendado para {encontro.data_hora.strftime('%d/%m/%Y, pelas %H:%M')}h. Se pretende adiar ou cancelar, contacte o sr Luis Maquina. Enviado por sistema."
                    )

                    await enviar_sms_api(mensagem_alerta, numeros_alerta)

                    await db.execute(
                        update(Encontro)
                        .where(Encontro.id == encontro.id)
                        .values(alerta_enviado="SIM")
                    )
                    await db.commit()
                    print(f"✅ Alerta enviado para encontro {encontro.id}")

                # ==========================
                # 📢 CONVOCATÓRIA (1 dia antes)
                # ==========================
                momento_convocatoria = encontro.data_hora - timedelta(days=1)
                if encontro.convocatoria_enviada == "NAO" and agora >= momento_convocatoria:
                    # Numeros para convocatória
                    if encontro.tipo == "PROFESSORES":
                        numeros_convocatoria = await pegar_numeros("professores")  # Para professores, números da tabela de professores
                        mensagem_convocatoria = (
                            f"Saudacoes prezados colegas, a direccao da EP-Phandira-2, vem por meio desta, convocar todos os professores desta instituicao, para participar numa reuniao, referente a {encontro.titulo}, a ter lugar amanha, dia {encontro.data_hora.strftime('%d/%m/%Y, pelas %H:%M')}h, na sala numero 5 da institucao anteriormente referida. Pede-se a pontualidade. DAP: Luis Maquina"
                        )
                    elif encontro.tipo == "FUNCIONARIOS":
                        numeros_convocatoria = await pegar_numeros("funcionarios")  # Para funcionários, números da tabela de funcionários
                        mensagem_convocatoria = (
                            f"Saudacoes, a direccao da EP-Phandira-2, vem por meio desta, convocar todos os funcionarios desta instituicao, para participar numa reuniao, referente a {encontro.titulo}, a ter lugar amanha, dia {encontro.data_hora.strftime('%d/%m/%Y, pelas %H:%M')}h, na sala numero 5 da institucao anteriormente referida. Pede-se a pontualidade. DE: Belinha Alfredo"
                        )
                    else:
                        continue  # ignora tipo desconhecido

                    await enviar_sms_api(mensagem_convocatoria, numeros_convocatoria)

                    await db.execute(
                        update(Encontro)
                        .where(Encontro.id == encontro.id)
                        .values(convocatoria_enviada="SIM")
                    )
                    await db.commit()
                    print(f"📢 Convocatória enviada para encontro {encontro.id}")

        # Espera próximo loop
        await asyncio.sleep(INTERVALO_VERIFICACAO)