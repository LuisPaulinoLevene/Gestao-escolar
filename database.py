from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# -----------------------------
# Neon Postgres URL (sem sslmode na string)
# -----------------------------
DATABASE_URL = "postgresql+asyncpg://neondb_owner:npg_sAcdx2MlNm0T@ep-jolly-recipe-aijktfrg-pooler.c-4.us-east-1.aws.neon.tech/neondb"

# -----------------------------
# Criando engine assíncrona
# -----------------------------
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_size=5,       # máximo de conexões simultâneas
    max_overflow=0,    # evita criar conexões extras
    connect_args={"ssl": True}  # SSL obrigatório no Neon
)

# -----------------------------
# Criando sessão assíncrona
# -----------------------------
SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# -----------------------------
# Base para os modelos
# -----------------------------
Base = declarative_base()

# -----------------------------
# Dependency para FastAPI
# -----------------------------
async def get_db():
    """
    Retorna uma sessão assíncrona para uso nos endpoints do FastAPI.
    """
    async with SessionLocal() as session:
        yield session
