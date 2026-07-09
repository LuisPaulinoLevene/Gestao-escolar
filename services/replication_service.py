from sqlalchemy import text

from database.primary import PrimarySession
from database.secondary import SecondarySession

from models.sync_event import SyncEvent


# =====================================================
# ESCOLHER BANCO DESTINO
# =====================================================

async def banco_destino(origem):

    if origem == "PRIMARY":
        return SecondarySession

    if origem == "SECONDARY":
        return PrimarySession

    return None



# =====================================================
# BUSCAR EVENTOS PENDENTES
# =====================================================

async def buscar_eventos():

    async with PrimarySession() as db:

        result = await db.execute(
            text("""
                SELECT 
                    id,
                    tabela,
                    registro_id,
                    operacao,
                    dados,
                    banco_origem
                FROM sync_events
                WHERE sincronizado = false
                ORDER BY id
            """)
        )

        return result.fetchall()



# =====================================================
# EXECUTAR INSERT
# =====================================================

async def executar_insert(
    session,
    tabela,
    dados
):

    campos = ", ".join(dados.keys())

    valores = ", ".join(
        [
            f":{campo}"
            for campo in dados.keys()
        ]
    )


    sql = text(
        f"""
        INSERT INTO {tabela}
        ({campos})
        VALUES
        ({valores})
        ON CONFLICT DO NOTHING
        """
    )


    await session.execute(
        sql,
        dados
    )



# =====================================================
# EXECUTAR UPDATE
# =====================================================

async def executar_update(
    session,
    tabela,
    registro_id,
    dados
):

    campos = [
        f"{campo}=:{campo}"
        for campo in dados.keys()
        if campo != "id"
    ]


    sql = text(
        f"""
        UPDATE {tabela}
        SET {','.join(campos)}
        WHERE id=:id
        """
    )


    dados["id"] = registro_id


    await session.execute(
        sql,
        dados
    )



# =====================================================
# EXECUTAR DELETE
# =====================================================

async def executar_delete(
    session,
    tabela,
    registro_id
):

    sql = text(
        f"""
        DELETE FROM {tabela}
        WHERE id=:id
        """
    )


    await session.execute(
        sql,
        {
            "id": registro_id
        }
    )



# =====================================================
# REPLICAR EVENTOS
# =====================================================

async def replicar_eventos():


    eventos = await buscar_eventos()


    if not eventos:

        return {
            "status": "sem eventos"
        }



    total = 0



    for evento in eventos:


        destino = await banco_destino(
            evento.banco_origem
        )


        if not destino:

            continue



        try:

            async with destino() as db:


                if evento.operacao == "INSERT":

                    await executar_insert(
                        db,
                        evento.tabela,
                        evento.dados
                    )


                elif evento.operacao == "UPDATE":

                    await executar_update(
                        db,
                        evento.tabela,
                        evento.registro_id,
                        evento.dados
                    )


                elif evento.operacao == "DELETE":

                    await executar_delete(
                        db,
                        evento.tabela,
                        evento.registro_id
                    )



                await db.commit()



            # marcar evento como sincronizado

            async with PrimarySession() as db:


                await db.execute(
                    text("""
                    UPDATE sync_events
                    SET sincronizado=true
                    WHERE id=:id
                    """),
                    {
                        "id": evento.id
                    }
                )


                await db.commit()



            total += 1



        except Exception as erro:

            print(
                "Erro ao replicar:",
                erro
            )



    return {
        "status": "ok",
        "replicados": total
    }