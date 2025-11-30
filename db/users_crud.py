import aiosqlite
from logs.logger import logger

async def create_user(id_tg: int):
    async with aiosqlite.connect('lead.db') as conn:
        await conn.execute('INSERT INTO users (id_tg) VALUES (?)', (id_tg,))
        await conn.commit()
    return True

async def get_user(id_tg: int):
    async with aiosqlite.connect('lead.db') as conn:
        cursor = await conn.execute('SELECT * FROM users WHERE id_tg = ?', (id_tg,))
        return await cursor.fetchone()
    return None

async def update_user(id_tg: int, **kwargs):
    print(kwargs.items())
    async with aiosqlite.connect('lead.db') as conn:
        for parameter, value in kwargs.items():
            await conn.execute(f'UPDATE users SET {parameter} = ? WHERE id_tg = ?', (value, id_tg))
        await conn.commit()
    return True

async def create_user_tag(user_id: int, tag_id: int):
    async with aiosqlite.connect('lead.db') as conn:
        try:
            await conn.execute(
                'INSERT INTO user_tags (user_id, tag_id) VALUES (?, ?)', 
                (user_id, tag_id)
            )
            await conn.commit()
            logger.info(f"✅ Добавлен тег {tag_id} пользователю {user_id}")
            return True
        except aiosqlite.IntegrityError as e:
            logger.error(f"❌ Ошибка добавления тега: {e}")
            return False

async def delete_user_tag(user_id: int, tag_id: int):
    async with aiosqlite.connect('lead.db') as conn:
        cursor = await conn.execute(
            'DELETE FROM user_tags WHERE user_id = ? AND tag_id = ?', 
            (user_id, tag_id)
        )
        await conn.commit()
        deleted_count = cursor.rowcount
        if deleted_count > 0:
            logger.info(f"✅ Удален тег {tag_id} у пользователя {user_id}")
        else:
            logger.warning(f"⚠️ Тег {tag_id} не найден у пользователя {user_id}")
        return deleted_count > 0

async def get_user_tags(user_id: int):
    async with aiosqlite.connect('lead.db') as conn:
        cursor = await conn.execute('''
            SELECT t.id, t.name 
            FROM tags t 
            JOIN user_tags ut ON t.id = ut.tag_id 
            WHERE ut.user_id = ?
        ''', (user_id,))
        return await cursor.fetchall()

async def get_tag_id_by_name(tag_name: str):
    async with aiosqlite.connect('lead.db') as conn:
        cursor = await conn.execute(
            'SELECT id FROM tags WHERE name = ?', 
            (tag_name,)
        )
        result = await cursor.fetchone()
        return result[0] if result else None
    
async def get_user_stats():
    """Получает статистику по пользователям и тегам"""
    async with aiosqlite.connect('lead.db') as conn:
        # Общее количество пользователей
        cursor = await conn.execute('SELECT COUNT(*) FROM users')
        total_users = (await cursor.fetchone())[0]
        
        # Количество пользователей по тегам
        cursor = await conn.execute('''
            SELECT t.name, COUNT(ut.user_id) as user_count
            FROM tags t 
            LEFT JOIN user_tags ut ON t.id = ut.tag_id 
            GROUP BY t.name
        ''')
        tag_stats = await cursor.fetchall()
        
        return total_users, dict(tag_stats)

