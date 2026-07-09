from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession
)

from sqlalchemy.orm import (
    declarative_base,
    sessionmaker
)


# ==========================
# URL BANCO PRINCIPAL
# ==========================

DATABASE_URL_PRIMARY = (
    "postgresql+asyncpg://neondb_owner:"
    "npg_sAcdx2MlNm0T@"
    "ep-jolly-recipe-aijktfrg-pooler.c-4.us-east-1.aws.neon.tech/"
    "neondb"
)


# ==========================
# ENGINE PRINCIPAL
# ==========================

engine_primary = create_async_engine(
    DATABASE_URL_PRIMARY,
    echo=False,
    pool_size=5,
    max_overflow=0,
    connect_args={
        "ssl": True
    }
)


# ==========================
# BASE DOS MODELOS
# ==========================

Base = declarative_base()


# ==========================
# SESSION PRINCIPAL
# ==========================

PrimarySession = sessionmaker(
    bind=engine_primary,
    class_=AsyncSession,
    expire_on_commit=False
)