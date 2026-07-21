import asyncio
import asyncpg

OLD_DB = "postgresql://neondb_owner:npg_sAcdx2MlNm0T@ep-jolly-recipe-aijktfrg-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require"
NEW_DB = "postgresql://neondb_owner:npg_Tke0clIxg7qt@ep-jolly-block-atgj0nyo-pooler.c-9.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

async def create_table(old_conn, new_conn, table):
    # Obter as colunas da tabela
    columns = await old_conn.fetch("""
        SELECT
            column_name,
            data_type,
            is_nullable,
            column_default
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = $1
        ORDER BY ordinal_position
    """, table)

    if not columns:
        print(f"⚠ Não foi possível obter as colunas da tabela {table}")
        return

    defs = []

    for c in columns:
        col = f'"{c["column_name"]}" {c["data_type"]}'

        if c["column_default"]:
            col += f' DEFAULT {c["column_default"]}'

        if c["is_nullable"] == "NO":
            col += " NOT NULL"

        defs.append(col)

    create_sql = f'''
    CREATE TABLE IF NOT EXISTS "{table}" (
        {", ".join(defs)}
    )
    '''

    await new_conn.execute(create_sql)


async def migrate():
    print("🚀 A ligar aos bancos...")

    old = await asyncpg.connect(OLD_DB)
    new = await asyncpg.connect(NEW_DB)

    tables = await old.fetch("""
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = 'public'
        ORDER BY tablename
    """)

    print(f"📦 {len(tables)} tabelas encontradas")

    for t in tables:
        table = t["tablename"]

        print(f"\n🛠 Criando tabela: {table}")
        await create_table(old, new, table)

        rows = await old.fetch(f'SELECT * FROM "{table}"')

        if not rows:
            print("   (Tabela vazia)")
            continue

        columns = list(rows[0].keys())

        cols = ",".join(f'"{c}"' for c in columns)
        placeholders = ",".join(f"${i+1}" for i in range(len(columns)))

        sql = f'''
            INSERT INTO "{table}" ({cols})
            VALUES ({placeholders})
        '''

        print(f"📥 Copiando {len(rows)} registos...")

        for row in rows:
            values = [row[c] for c in columns]
            await new.execute(sql, *values)

        print("✅ Concluído")

    await old.close()
    await new.close()

    print("\n🎉 Migração terminada com sucesso!")

if __name__ == "__main__":
    asyncio.run(migrate())