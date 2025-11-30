import aiosqlite


async def create_table(app):
    conn = await aiosqlite.connect("lead.db")
    await conn.execute("""CREATE TABLE IF NOT EXISTS users(
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       id_tg INTEGER UNIQUE,
                       name TEXT NULL,
                       phone TEXT NULL,
                       email TEXT NULL,
                       agreement INTEGER DEFAULT 0,
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
    if num[0] == 0:
        await conn.execute(
            '''INSERT OR IGNORE INTO tags (name) VALUES ('Горячий'), ('Обычный'), ('Холодный')'''
        )

    await conn.commit()
    await conn.close()
