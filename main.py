import os
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

# Importe suas rotas, banco de dados e outras configurações
from database import Base, engine
from routers import professor, aluno, classe, turma, matricula, admin, dap, director, chefe_secretaria, funcionario_secretaria, usuario_professor, dashboard, importar_alunos
from routers.pages import ep_phandira_2, dados_aluno


is_production = os.getenv("ENV") == "production"


app = FastAPI(
    title="Sistema de Gestão Escolar EP-Phandira-2",
    docs_url=None if is_production else "/docs",
    redoc_url=None if is_production else "/redoc" 
)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Rota raiz → redireciona para /auth
@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/ep_phandira_2")

# API routes
app.include_router(professor.router, prefix="/api")

# HTML pages
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
