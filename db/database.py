import aiosqlite

async def create_table(app):
    conn = await aiosqlite.connect('lead.db')
    await conn.execute('''CREATE TABLE IF NOT EXISTS users(
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       id_tg INTEGER UNIQUE,
                       name TEXT NULL,
                       phone TEXT NULL,
                       email TEXT NULL,
                       agreement INTEGER DEFAULT 0,
                       created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    await conn.commit()
    await conn.close()