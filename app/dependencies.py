from providers import DB


async def get_psql() -> DB:
    db = DB()
    return db
