from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession
)

from sqlalchemy.orm import sessionmaker


DATABASE_SECONDARY = (
    "postgresql+asyncpg://neondb_owner:"
    "npg_Tke0clIxg7qt@"
    "ep-jolly-block-atgj0nyo-pooler.c-9.us-east-1.aws.neon.tech/"
    "neondb"
)


engine_secondary = create_async_engine(
    DATABASE_SECONDARY,
    echo=False,
    pool_size=5,
    max_overflow=10,
    connect_args={
        "ssl": True
    }
)



SecondarySession = sessionmaker(
    bind=engine_secondary,
    class_=AsyncSession,
    expire_on_commit=False
)



async def get_secondary():

    async with SecondarySession() as session:
        yield session