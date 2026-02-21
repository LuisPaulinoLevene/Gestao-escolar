import os
import asyncio
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

# Banco de dados
from database import Base, engine

# Routers
from routers import (
    professor, aluno, classe, turma, matricula, admin, dap,
    director, chefe_secretaria, funcionario_secretaria, usuario_professor,
    dashboard, importar_alunos, sms, encontro, contactos
)
from routers.pages import ep_phandira_2, dados_aluno, encontros, contacto, informacoes

# 🔥 IMPORTA O MONITOR AUTOMÁTICO
from services.monitor_encontros import monitorar_encontros


# Verifica ambiente
is_production = os.getenv("ENV") == "production"

# Cria app
app = FastAPI(
    title="Sistema de Gestão Escolar EP-Phandira-2",
    docs_url=None if is_production else "/docs",
    redoc_url=None if is_production else "/redoc"
)

# ==========================
# Evento startup
# ==========================
@app.on_event("startup")
async def startup():
    # Cria tabelas no banco
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 🔥 INICIA MONITOR AUTOMÁTICO EM BACKGROUND
    asyncio.create_task(monitorar_encontros())

    print("✅ Sistema iniciado com monitor automático de encontros")


# ==========================
# Rota raiz → redireciona
# ==========================
@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/ep_phandira_2")


# ==========================
# API routes
# ==========================
app.include_router(professor.router, prefix="/api")


# ==========================
# HTML pages
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
