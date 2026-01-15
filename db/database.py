import aiosqlite
from config.config import TAGS

async def create_table(app):
    conn = await aiosqlite.connect("lead.db")
    await conn.execute("""CREATE TABLE IF NOT EXISTS users(
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   id_tg INTEGER UNIQUE,
                   name TEXT NULL,
                   phone TEXT NULL,
                   email TEXT NULL,
                   agreement INTEGER DEFAULT 0,
                   visit_count INTEGER DEFAULT 1,
                   last_visit DATETIME DEFAULT CURRENT_TIMESTAMP,
                   created_at DATETIME DEFAULT CURRENT_TIMESTAMP)""")

    await conn.execute("""CREATE TABLE IF NOT EXISTS tags(
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT UNIQUE)""")

    await conn.execute('''CREATE TABLE IF NOT EXISTS user_tags(
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER,
                            tag_id INTEGER,
                            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                            FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE)''')

    cur = await conn.execute("SELECT COUNT(*) FROM tags")
    num = await cur.fetchone()
    if num[0] < len(TAGS):
        stmt = 'INSERT OR IGNORE INTO tags (name) VALUES (?)'
        for tag in TAGS:
            await conn.execute(stmt, (tag,))

    await conn.commit()
    await conn.close()
