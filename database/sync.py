from database.primary import PrimarySession
from database.secondary import SecondarySession

from models.sync_event import SyncEvent



async def sincronizar():

    async with SecondarySession() as secundaria:


        eventos = await secundaria.execute(
            SyncEvent.__table__.select()
            .where(
                SyncEvent.sincronizado == False
            )
        )


        eventos = eventos.fetchall()



        for evento in eventos:


            async with PrimarySession() as principal:


                # aqui executamos INSERT/UPDATE
                # conforme a tabela


                evento.sincronizado = True


                await secundaria.commit()