from app.database.connection import get_db


async def create_tables():
    db = await get_db()

    await db.execute("""
    CREATE TABLE IF NOT EXISTS users(
        user_id INTEGER PRIMARY KEY,
        full_name TEXT,
        username TEXT,
        phone TEXT,
        join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    await db.commit()
    await db.close()


async def add_user(user_id, full_name, username):

    db = await get_db()

    await db.execute("""
    INSERT OR IGNORE INTO users
    (user_id, full_name, username)
    VALUES(?,?,?)
    """,(user_id, full_name, username))

    await db.commit()
    await db.close()