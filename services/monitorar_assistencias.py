import os
import asyncio
from datetime import datetime, timedelta
import httpx
from sqlalchemy import select, update
from database import SessionLocal
from models.assistencia import AssistenciaMutua
from models.contactos_professores import ContactoProfessor

# Intervalo de verificação do loop (em segundos)
INTERVALO_VERIFICACAO = 30  # checa a cada 30 segundos

# ==========================
# Função para enviar SMS via endpoint
# ==========================
async def enviar_sms_api(mensagem, numeros):
    base_url = os.getenv("RENDER_EXTERNAL_URL", "http://127.0.0.1:8000")
    url = f"{base_url}/sms/enviar"

    payload = {
        "sender_id": "PHANDIRA-2",
        "mensagem": mensagem,
        "numeros": numeros  # Aqui garantimos que é uma lista de números
    }

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(url, json=payload)
            if resp.status_code != 200:
                print(f"⚠️ Erro ao enviar SMS: {resp.text}")
        except Exception as e:
            print(f"⚠️ Exception ao enviar SMS: {e}")

# ==========================
# Monitor de assistências
# ==========================
async def monitorar_assistencias():
    print("🔄 Monitor automático de assistências iniciado")

    while True:
        agora = datetime.now()
        amanha = agora + timedelta(days=1)
        dia_amanha = amanha.date()

        async with SessionLocal() as db:
            # Seleciona todas assistências programadas para amanhã
            result = await db.execute(
                select(AssistenciaMutua)
                .where(
                    AssistenciaMutua.data_hora >= datetime.combine(dia_amanha, datetime.min.time()),
                    AssistenciaMutua.data_hora <= datetime.combine(dia_amanha, datetime.max.time())
                )
            )
            assistencias = result.scalars().all()

            for a in assistencias:
                # ==========================
                # Ignora se o status for NAO
                # ==========================
                if a.status_aprovacao == "NAO":
                    continue  # passa para a próxima assistencia

                # Pegar contatos do professor assistido
                result_assistido = await db.execute(
                    select(ContactoProfessor)
                    .where(ContactoProfessor.nome == a.professor_assistido_nome)
                )
                professor_assistido = result_assistido.scalars().first()

                # Pegar contatos do professor assistente
                result_assistente = await db.execute(
                    select(ContactoProfessor)
                    .where(ContactoProfessor.nome == a.professor_assistente_nome)
                )
                professor_assistente = result_assistente.scalars().first()

                # ==========================
                # Enviar SMS para o professor assistido
                # ==========================
                if professor_assistido:
                    mensagem_assistido = (
                        f"Saudacoes, amanha dia {a.data_hora.strftime('%d/%m/%Y')} tera uma assistencia de aula da disciplina de {a.disciplina} pelas {a.data_hora.strftime('%H:%M')}h, pelo professor {a.professor_assistente_nome}. Bom trabalho."
                    )
                    await enviar_sms_api(mensagem_assistido, [professor_assistido.telefone])  # Envia para um número de cada vez
                    await asyncio.sleep(30)  # Pausa de 30 segundos entre os envios

                # ==========================
                # Enviar SMS para o professor assistente
                # ==========================
                if professor_assistente:
                    mensagem_assistente = (
                        f"Saudacoes, amanha dia {a.data_hora.strftime('%d/%m/%Y')} pela {a.data_hora.strftime('%H:%M')}h, devera efectuar uma assistencia de aula de {a.disciplina}, na {a.classe} classe, turma {a.turma}, ao professor {a.professor_assistido_nome}, na sala numero {a.numero_sala}, localizada na {a.localizacao_sala}."
                    )
                    await enviar_sms_api(mensagem_assistente, [professor_assistente.telefone])  # Envia para um número de cada vez
                    await asyncio.sleep(30)  # Pausa de 30 segundos entre os envios

                # ==========================
                # Atualiza o status para NAO para não enviar novamente
                # ==========================
                await db.execute(
                    update(AssistenciaMutua)
                    .where(AssistenciaMutua.id == a.id)
                    .values(status_aprovacao="NAO")
                )
                await db.commit()
                print(f"✅ Lembrete enviado e status atualizado para NAO (Assistência ID {a.id})")

        # Espera próximo loop
        await asyncio.sleep(INTERVALO_VERIFICACAO)