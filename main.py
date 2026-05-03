# main.py
import os
import asyncio
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

# Banco de dados
from database import Base, engine

# Routers API e Pages
from routers import (
    professor, aluno, classe, turma, matricula, admin, dap,
    director, chefe_secretaria, funcionario_secretaria, usuario_professor,
    dashboard, importar_alunos, sms, encontro, contactos, assistencias,
    mozesms, encontro_coletivo, outros_encontros,  disciplina
)

from routers.pages import (
    ep_phandira_2, dados_aluno, encontros, contacto, informacoes,
    assistencia, ass_direccao, comprar_creditos,
    encontros_coletivo, outro_encontro, classes, turmas, disciplinas
)

from routers.assistencia_direcao import router as assistencia_direcao_router

# 🔥 Monitores (importação apenas)
from services.monitor_encontros import monitorar_encontros
from services.monitorar_assistencias import monitorar_assistencias
from services.monitor_ass_direcao import monitorar_assistencias_direcao as monitor_ass_direcao
from services.monitor_encontro_coletivo import monitorar_encontros_coletivo
from services.monitor_outros_encontros import monitorar_outros_encontros

# ==========================
# Configuração ambiente
# ==========================
is_production = os.getenv("ENV") == "production"

app = FastAPI(
    title="Sistema de Gestão de SMS",
    docs_url=None if is_production else "/docs",
    redoc_url=None if is_production else "/redoc"
)

# ==========================
# CORS
# ==========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",
        "https://ep-phandira-2.onrender.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================
# STARTUP (SEM MONITORES)
# ==========================
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("✅ Sistema iniciado (modo cron ativo)")


# ========================
# ROTA RAIZ
# ========================
@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/ep_phandira_2")


# ==========================
# 🔥 ROTAS MANUAIS DOS MONITORES
# ==========================

@app.get("/monitor/encontros")
async def run_encontros():
    await monitorar_encontros()
    return {"status": "encontros executado"}


@app.get("/monitor/assistencias")
async def run_assistencias():
    await monitorar_assistencias()
    return {"status": "assistencias executado"}


@app.get("/monitor/ass-direcao")
async def run_ass_direcao():
    await monitor_ass_direcao()
    return {"status": "assistencia direção executado"}


@app.get("/monitor/coletivo")
async def run_coletivo():
    await monitorar_encontros_coletivo()
    return {"status": "coletivo executado"}


@app.get("/monitor/outros")
async def run_outros():
    await monitorar_outros_encontros()
    return {"status": "outros encontros executado"}



# ==========================
# API ROUTES
# ==========================
app.include_router(professor.router)
app.include_router(assistencia_direcao_router)
app.include_router(aluno.router)
app.include_router(classe.router)
app.include_router(turma.router)
app.include_router(matricula.router)
app.include_router(admin.router)
app.include_router(dap.router)
app.include_router(director.router)
app.include_router(chefe_secretaria.router)
app.include_router(funcionario_secretaria.router)
app.include_router(usuario_professor.router)
app.include_router(dashboard.router)
app.include_router(importar_alunos.router)
app.include_router(sms.router)
app.include_router(encontro.router)
app.include_router(contactos.router)
app.include_router(encontros.router)
app.include_router(contacto.router)
app.include_router(informacoes.router)
app.include_router(assistencias.router)
app.include_router(assistencia.router)
app.include_router(ass_direccao.router)
app.include_router(mozesms.router)
app.include_router(encontro_coletivo.router)
app.include_router(outros_encontros.router)
app.include_router(disciplina.router)


# ==========================
# HTML PAGES
# ==========================
app.include_router(ep_phandira_2.router)
app.include_router(aluno.router)
app.include_router(classe.router)
app.include_router(turma.router)
app.include_router(matricula.router)
app.include_router(admin.router)
app.include_router(dap.router)
app.include_router(director.router)
app.include_router(chefe_secretaria.router)
app.include_router(funcionario_secretaria.router)
app.include_router(usuario_professor.router)
app.include_router(dashboard.router)
app.include_router(dados_aluno.router)
app.include_router(importar_alunos.router)
app.include_router(sms.router)
app.include_router(encontro.router)
app.include_router(contactos.router)
app.include_router(encontros.router)
app.include_router(contacto.router)
app.include_router(informacoes.router)
app.include_router(assistencias.router)
app.include_router(assistencia.router)
app.include_router(ass_direccao.router)
app.include_router(comprar_creditos.router)
app.include_router(encontro_coletivo.router)
app.include_router(outro_encontro.router)
app.include_router(classes.router)
app.include_router(turmas.router)
app.include_router(disciplinas.router)

# ==========================
# FIM
# ==========================