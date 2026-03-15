import os
import asyncio
from datetime import datetime, timedelta
import httpx
from sqlalchemy import select, update
from database import SessionLocal
from models.assistencia import AssistenciaMutua
from models.contactos_professores import ContactoProfessor

INTERVALO_VERIFICACAO = 30


# ==========================
# Função enviar SMS
# ==========================
async def enviar_sms_api(mensagem, numeros):
    base_url = os.getenv("RENDER_EXTERNAL_URL", "http://127.0.0.1:8000")
    url = f"{base_url}/sms/enviar"

    payload = {
        "sender_id": "PHANDIRA-2",
        "mensagem": mensagem,
        "numeros": numeros
    }

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(url, json=payload)
            print(f"Resposta SMS: {resp.status_code} - {resp.text}")
        except Exception as e:
            print(f"⚠️ Erro ao enviar SMS: {e}")


# ==========================
# Monitor
# ==========================
async def monitorar_assistencias():

    print("🔄 Monitor automático iniciado")

    while True:

        agora = datetime.now()
        hoje = agora.date()
        amanha = hoje + timedelta(days=1)

        print(f"\n📅 Hoje: {hoje}")
        print(f"📅 Verificando assistências para amanhã: {amanha}")

        async with SessionLocal() as db:

            # Busca assistências aprovadas
            result = await db.execute(
                select(AssistenciaMutua)
                .where(
                    AssistenciaMutua.status_aprovacao == "APROVADO"
                )
            )

            assistencias = result.scalars().all()

            print(f"Assistências encontradas: {len(assistencias)}")

            for a in assistencias:

                data_assistencia = a.data_hora.date()

                print(
                    f"🔎 Assistência ID {a.id} - Data: {data_assistencia}"
                )

                # ==========================
                # VERIFICA SE É PARA AMANHÃ
                # ==========================
                if data_assistencia != amanha:
                    print("⏭️ Não é para amanhã. Ignorando.")
                    continue

                print("📨 Assistência é para amanhã. Enviando SMS...")

                # ==========================
                # BUSCAR PROFESSOR ASSISTIDO
                # ==========================
                result_assistido = await db.execute(
                    select(ContactoProfessor)
                    .where(
                        ContactoProfessor.nome == a.professor_assistido_nome
                    )
                )

                professor_assistido = result_assistido.scalars().first()

                # ==========================
                # BUSCAR PROFESSOR ASSISTENTE
                # ==========================
                result_assistente = await db.execute(
                    select(ContactoProfessor)
                    .where(
                        ContactoProfessor.nome == a.professor_assistente_nome
                    )
                )

                professor_assistente = result_assistente.scalars().first()

                # ==========================
                # SMS PROFESSOR ASSISTIDO
                # ==========================
                if professor_assistido:

                    mensagem = (
                        f"Saudacoes. Amanha dia {a.data_hora.strftime('%d/%m/%Y')} "
                        f"tera uma assistencia de aula da disciplina de {a.disciplina} "
                        f"pelas {a.data_hora.strftime('%H:%M')}h, pelo professor "
                        f"{a.professor_assistente_nome}. Bom trabalho."
                    )

                    print(f"📲 Enviando SMS para assistido: {professor_assistido.telefone}")

                    await enviar_sms_api(
                        mensagem,
                        [professor_assistido.telefone]
                    )

                    await asyncio.sleep(30)

                else:
                    print("⚠️ Professor assistido não encontrado")

                # ==========================
                # SMS PROFESSOR ASSISTENTE
                # ==========================
                if professor_assistente:

                    mensagem = (
                        f"Saudacoes. Amanha dia {a.data_hora.strftime('%d/%m/%Y')} "
                        f"pela {a.data_hora.strftime('%H:%M')}h devera efectuar "
                        f"uma assistencia de aula de {a.disciplina}, na "
                        f"{a.classe} classe, turma {a.turma}, ao professor "
                        f"{a.professor_assistido_nome}, na sala numero "
                        f"{a.numero_sala}, localizada na {a.localizacao_sala}."
                    )

                    print(f"📲 Enviando SMS para assistente: {professor_assistente.telefone}")

                    await enviar_sms_api(
                        mensagem,
                        [professor_assistente.telefone]
                    )

                    await asyncio.sleep(30)

                else:
                    print("⚠️ Professor assistente não encontrado")

                # ==========================
                # MARCAR COMO ENVIADO
                # ==========================
                await db.execute(
                    update(AssistenciaMutua)
                    .where(AssistenciaMutua.id == a.id)
                    .values(status_aprovacao="NAO")
                )

                await db.commit()

                print(f"✅ SMS enviado. Assistência {a.id} atualizada.")

        await asyncio.sleep(INTERVALO_VERIFICACAO)


# ==========================
# MAIN
# ==========================
async def main():
    await monitorar_assistencias()


if __name__ == "__main__":
    asyncio.run(main())
