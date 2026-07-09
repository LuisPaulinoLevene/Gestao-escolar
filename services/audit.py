import json

from sqlalchemy import event, inspect

from models.sync_event import SyncEvent



# ==========================================
# Serialize object
# ==========================================
def serializar(obj):

    dados = {}

    for coluna in inspect(obj).mapper.column_attrs:

        valor = getattr(
            obj,
            coluna.key
        )

        try:

            json.dumps(valor)

            dados[coluna.key] = valor


        except Exception:

            dados[coluna.key] = str(valor)


    return dados



# ==========================================
# Get database origin
# ==========================================
def origem_banco(connection):

    try:

        return connection.info.get(
            "banco_origem",
            "UNKNOWN"
        )


    except Exception:

        return "UNKNOWN"




# ==========================================
# AFTER INSERT
# ==========================================
def after_insert(mapper, connection, target):

    connection.execute(

        SyncEvent.__table__.insert().values(

            tabela=target.__tablename__,


            # mantém como STRING
            registro_id=str(
                target.id
            ),


            operacao="INSERT",


            dados=serializar(
                target
            ),


            banco_origem=origem_banco(
                connection
            ),


            sincronizado=False
        )
    )





# ==========================================
# AFTER UPDATE
# ==========================================
def after_update(mapper, connection, target):

    connection.execute(

        SyncEvent.__table__.insert().values(

            tabela=target.__tablename__,


            registro_id=str(
                target.id
            ),


            operacao="UPDATE",


            dados=serializar(
                target
            ),


            banco_origem=origem_banco(
                connection
            ),


            sincronizado=False
        )
    )





# ==========================================
# AFTER DELETE
# ==========================================
def after_delete(mapper, connection, target):

    connection.execute(

        SyncEvent.__table__.insert().values(

            tabela=target.__tablename__,


            registro_id=str(
                target.id
            ),


            operacao="DELETE",


            dados={
                "id": target.id
            },


            banco_origem=origem_banco(
                connection
            ),


            sincronizado=False
        )
    )





# ==========================================
# Register listeners
# ==========================================
def registrar_auditoria(Base):

    for mapper in Base.registry.mappers:

        model = mapper.class_


        if model.__tablename__ == "sync_events":

            continue



        event.listen(
            model,
            "after_insert",
            after_insert
        )


        event.listen(
            model,
            "after_update",
            after_update
        )


        event.listen(
            model,
            "after_delete",
            after_delete
        )