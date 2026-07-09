from sqlalchemy import text
from sqlalchemy import event
from sqlalchemy.orm import Session

from .primary import (
    Base,
    PrimarySession,
    engine_primary
)

from .secondary import (
    SecondarySession
)


# ===========================================
# Verifica se um banco está disponível
# ===========================================
async def banco_disponivel(session_factory):

    try:
        async with session_factory() as db:

            await db.execute(
                text("SELECT 1")
            )

            return True

    except Exception:
        return False


# ===========================================
# Escolhe automaticamente o banco
# ===========================================
async def escolher_banco():

    principal = await banco_disponivel(
        PrimarySession
    )

    if principal:
        print("Banco principal ativo")
        return PrimarySession, "PRIMARY"


    secundario = await banco_disponivel(
        SecondarySession
    )

    if secundario:
        print("Banco secundário ativo")
        return SecondarySession, "SECONDARY"


    raise Exception(
        "Nenhum banco disponível"
    )


# ===========================================
# Dependency do FastAPI
# ===========================================
async def get_db():

    SessionFactory, origem = await escolher_banco()

    async with SessionFactory() as session:

        # Guarda a origem do banco na sessão
        session.info["banco_origem"] = origem

        yield session


# ===========================================
# Copia session.info para connection.info
# usado pelos eventos de auditoria
# ===========================================
@event.listens_for(
    Session,
    "after_begin"
)
def _set_connection_info(
    session,
    transaction,
    connection
):

    connection.info["banco_origem"] = (
        session.info.get(
            "banco_origem",
            "UNKNOWN"
        )
    )


# ===========================================
# Compatibilidade com o projeto antigo
# ===========================================

# Mantém os imports antigos funcionando
SessionLocal = PrimarySession

engine = engine_primary