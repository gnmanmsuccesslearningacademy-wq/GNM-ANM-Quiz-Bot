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
async def update_phone(user_id, phone):

    db = await get_db()

    await db.execute(
        """
        UPDATE users
        SET phone = ?
        WHERE user_id = ?
        """,
        (phone, user_id)
    )

    await db.commit()
    await db.close()


async def get_user(user_id):

    db = await get_db()

    cursor = await db.execute(
        """
        SELECT * FROM users
        WHERE user_id = ?
        """,
        (user_id,)
    )

    user = await cursor.fetchone()

    await cursor.close()
    await db.close()

    return user