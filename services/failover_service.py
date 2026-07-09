from database.primary import engine_primary
from database.secondary import engine_secondary
from sqlalchemy import text


async def verificar_banco(engine):

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))

        return True

    except Exception:
        return False



async def status_bancos():

    primary_online = await verificar_banco(
        engine_primary
    )

    secondary_online = await verificar_banco(
        engine_secondary
    )


    return {
        "primary": {
            "online": primary_online
        },
        "secondary": {
            "online": secondary_online
        }
    }