from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from database import Base, engine
from routers import professor, aluno, classe, turma, matricula, admin, dap, director, chefe_secretaria, funcionario_secretaria, usuario_professor, login
from routers.pages import auth

app = FastAPI(title="Sitema de Gestao Escolar EP-Phandira-2")

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Rota raiz → redireciona para /dashboard
@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/auth")

# API routes
app.include_router(professor.router, prefix="/api")

# HTML pages
app.include_router(auth.router)
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
app.include_router(login.router)