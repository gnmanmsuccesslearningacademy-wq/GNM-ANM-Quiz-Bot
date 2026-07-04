import aiosqlite

DB_NAME = "data/database.db"


async def get_db():
    return await aiosqlite.connect(DB_NAME)