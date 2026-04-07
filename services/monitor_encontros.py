import os
import asyncio
from datetime import datetime, timedelta
import httpx
from sqlalchemy import select, update
from database import SessionLocal
from models.encontro import Encontro
from models.configuracao import Configuracao
from routers.contactos import tipo_tabela

# ==========================
# 📩 Envio de SMS
# ==========================
async def enviar_sms_api(mensagem, numeros):
    base_url = os.getenv("RENDER_EXTERNAL_URL") or "http://127.0.0.1:8000"
    url = f"{base_url}/sms/enviar"

    if not isinstance(numeros, list):
        numeros = [numeros]

    payload = {
        "sender_id": "PHANDIRA-2",
        "mensagem": mensagem,
        "numeros": numeros
    }

    print("📡 URL:", url)
    print("📤 Enviando para:", numeros)

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.post(url, json=payload)
            print("📥 Status:", resp.status_code)
            return resp.status_code == 200
        except Exception as e:
            print(f"⚠️ Exception ao enviar SMS: {e}")
            return False

# ==========================
# 📞 Pegar números
# ==========================
async def pegar_numeros(tipo):
    if tipo not in tipo_tabela:
        return []

    Model = tipo_tabela[tipo]

    async with SessionLocal() as db:
        result = await db.execute(select(Model))
        contactos = result.scalars().all()
        numeros = [c.telefone for c in contactos if c.telefone]
        print(f"\n📞 [LOG] Tipo: {tipo}")
        print(f"📞 [LOG] Quantidade: {len(numeros)}")
        print(f"📞 [LOG] Números: {numeros}\n")
        return numeros

# ==========================
# ⏱️ Controle de execução (1x por hora)
# ==========================
async def pode_executar(db):
    result = await db.execute(
        select(Configuracao).where(Configuracao.chave == "ultima_verificacao_encontros")
    )
    config = result.scalar_one_or_none()
    agora = datetime.now()

    if config:
        ultima = config.valor_datetime
        if ultima and (agora - ultima).total_seconds() < 3600:
            print("⏳ Ainda não passou 1 hora, ignorando execução")
            return False
        config.valor_datetime = agora
    else:
        config = Configuracao(
            chave="ultima_verificacao_encontros",
            valor_datetime=agora
        )
        db.add(config)

    await db.commit()
    return True

# ==========================
# 🔄 Execução principal
# ==========================
async def monitorar_encontros():
    print("🔄 Execução de encontros")

    async with SessionLocal() as db:
        # 🔥 CONTROLE DE 1 HORA
        if not await pode_executar(db):
            return

        agora = datetime.now()
        print(f"\n📅 Verificando encontros em {agora}")

        result = await db.execute(
            select(Encontro).where(Encontro.status == "APROVADO")
        )
        encontros = result.scalars().all()

        for encontro in encontros:
            # ==========================
            # 🔔 ALERTA (2 dias antes)
            # ==========================
            momento_alerta = encontro.data_hora - timedelta(days=2)
            if encontro.alerta_enviado == "NAO" and agora >= momento_alerta:
                print(f"\n🔔 Enviando ALERTA para encontro {encontro.id}")

                if encontro.tipo == "PROFESSORES":
                    numeros_alerta = await pegar_numeros("diretor")
                elif encontro.tipo == "FUNCIONARIOS":
                    numeros_alerta = await pegar_numeros("direcao")
                else:
                    continue

                if numeros_alerta:
                    mensagem_alerta = (
                        f"Saudacoes, ha um encontro referente a {encontro.titulo}, "
                        f"agendado para {encontro.data_hora.strftime('%d/%m/%Y, pelas %H:%M')}h. "
                        f"Se pretende adiar ou cancelar, entre no sistema."
                    )
                    sucesso = await enviar_sms_api(mensagem_alerta, numeros_alerta)
                    if sucesso:
                        await db.execute(
                            update(Encontro)
                            .where(Encontro.id == encontro.id)
                            .values(alerta_enviado="SIM")
                        )
                        await db.commit()
                        print(f"✅ Alerta enviado (Encontro {encontro.id})")

            # ==========================
            # 📢 CONVOCATÓRIA (1 dia antes)
            # ==========================
            momento_convocatoria = encontro.data_hora - timedelta(days=1)
            if encontro.convocatoria_enviada == "NAO" and agora >= momento_convocatoria:
                print(f"\n📢 Enviando CONVOCATÓRIA para encontro {encontro.id}")

                if encontro.tipo == "PROFESSORES":
                    numeros_convocatoria = await pegar_numeros("professores")
                    mensagem_convocatoria = (
                        f"Saudacoes prezados colegas, a direccao da EP-Phandira-2 "
                        f"convoca todos os professores para reuniao referente a {encontro.titulo}, "
                        f"amanha dia {encontro.data_hora.strftime('%d/%m/%Y, pelas %H:%M')}h, "
                        f"na sala numero 5. Pede-se pontualidade. DAP: Luis Maquina"
                    )
                elif encontro.tipo == "FUNCIONARIOS":
                    numeros_convocatoria = await pegar_numeros("funcionarios")
                    mensagem_convocatoria = (
                        f"Saudacoes, a direccao da EP-Phandira-2 convoca todos os "
                        f"funcionarios para reuniao referente a {encontro.titulo}, "
                        f"amanha dia {encontro.data_hora.strftime('%d/%m/%Y, pelas %H:%M')}h, "
                        f"na sala numero 5. Pede-se pontualidade. DE: Belinha Alfredo"
                    )
                else:
                    continue

                enviados = 0
                total = len(numeros_convocatoria)

                for numero in numeros_convocatoria:
                    sucesso = await enviar_sms_api(mensagem_convocatoria, numero)
                    if sucesso:
                        enviados += 1
                    await asyncio.sleep(5)

                if total > 0 and enviados == total:
                    await db.execute(
                        update(Encontro)
                        .where(Encontro.id == encontro.id)
                        .values(convocatoria_enviada="SIM")
                    )
                    await db.commit()
                    print(f"📢 Convocatória enviada (Encontro {encontro.id})")
                else:
                    print(f"❌ Nem todos SMS foram enviados ({enviados}/{total})")

# ==========================
# 🚀 Inicialização
# ==========================
async def main():
    await monitorar_encontros()

if __name__ == "__main__":
    asyncio.run(main())
