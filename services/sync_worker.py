import asyncio
from datetime import datetime

from sqlalchemy import select

from database.primary import (
    PrimarySession,
    Base
)

from database.secondary import (
    SecondarySession
)

from models.sync_event import SyncEvent



# ==========================================
# Convert data types from JSON
# ==========================================
def convert_dates(data):

    data = dict(data)

    for key, value in data.items():

        if isinstance(value, str):

            try:

                data[key] = datetime.strptime(
                    value,
                    "%Y-%m-%d"
                ).date()


            except ValueError:

                pass


    return data





# ==========================================
# Destination database
# ==========================================
def get_destination_database(origin):

    if origin == "PRIMARY":

        return SecondarySession


    if origin == "SECONDARY":

        return PrimarySession


    return None





# ==========================================
# Find SQLAlchemy model
# ==========================================
def find_model(table_name):

    for mapper in Base.registry.mappers:

        model = mapper.class_


        if model.__tablename__ == table_name:

            return model


    return None





# ==========================================
# Get pending events
# ==========================================
async def fetch_pending_events():

    events = []



    # --------------------------
    # PRIMARY
    # --------------------------

    try:

        async with PrimarySession() as db:


            result = await db.execute(

                select(SyncEvent)

                .where(
                    SyncEvent.sincronizado == False
                )

            )


            primary_events = result.scalars().all()



            for event in primary_events:

                event.origin_database = "PRIMARY"



            events.extend(
                primary_events
            )


    except Exception as error:

        print(
            "PRIMARY unavailable:",
            error
        )





    # --------------------------
    # SECONDARY
    # --------------------------

    try:

        async with SecondarySession() as db:


            result = await db.execute(

                select(SyncEvent)

                .where(
                    SyncEvent.sincronizado == False
                )

            )


            secondary_events = result.scalars().all()



            for event in secondary_events:

                event.origin_database = "SECONDARY"



            events.extend(
                secondary_events
            )


    except Exception as error:

        print(
            "SECONDARY unavailable:",
            error
        )



    return events





# ==========================================
# Replicate event
# ==========================================
async def replicate_event(event):


    DestinationSession = get_destination_database(
        event.origin_database
    )


    if not DestinationSession:

        return False



    model = find_model(
        event.tabela
    )


    if not model:

        print(
            "Model not found:",
            event.tabela
        )

        return False





    async with DestinationSession() as db:



        # Convert ID
        try:

            record_id = int(
                event.registro_id
            )


        except Exception:

            record_id = event.registro_id





        # ==========================
        # INSERT
        # ==========================

        if event.operacao == "INSERT":


            result = await db.execute(

                select(model)

                .where(
                    model.id == record_id
                )

            )


            exists = result.scalar_one_or_none()



            if not exists:


                dados = convert_dates(
                    event.dados
                )


                new_record = model(
                    **dados
                )


                db.add(
                    new_record
                )





        # ==========================
        # UPDATE
        # ==========================

        elif event.operacao == "UPDATE":


            result = await db.execute(

                select(model)

                .where(
                    model.id == record_id
                )

            )


            record = result.scalar_one_or_none()



            if record:


                dados = convert_dates(
                    event.dados
                )



                for key, value in dados.items():


                    setattr(
                        record,
                        key,
                        value
                    )





        # ==========================
        # DELETE
        # ==========================

        elif event.operacao == "DELETE":


            result = await db.execute(

                select(model)

                .where(
                    model.id == record_id
                )

            )


            record = result.scalar_one_or_none()



            if record:

                await db.delete(
                    record
                )





        await db.commit()



    return True





# ==========================================
# Mark event as synchronized
# ==========================================
async def mark_as_synced(event_id, origin):


    Session = (

        PrimarySession

        if origin == "PRIMARY"

        else SecondarySession

    )



    async with Session() as db:


        event = await db.get(

            SyncEvent,

            event_id

        )


        if event:


            event.sincronizado = True


            await db.commit()





# ==========================================
# Process events
# ==========================================
async def process_events():


    events = await fetch_pending_events()



    for event in events:


        success = await replicate_event(
            event
        )


        if success:


            await mark_as_synced(

                event.id,

                event.origin_database

            )





# ==========================================
# Background worker
# ==========================================
async def start_sync_worker():


    print(
        "Sync Worker started..."
    )


    while True:


        try:


            await process_events()



        except Exception as error:


            print(
                "Sync Worker error:",
                error
            )



        await asyncio.sleep(
            10
        )