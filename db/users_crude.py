import aiosqlite

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

async def update_user(id_tg: int, **fields):
    
    if not fields:
        return False
    
    async with aiosqlite.connect('lead.db') as conn:
        set_parts = []
        values = []
        
        for field_name, field_value in fields.items():
            set_parts.append(f"{field_name} = ?")  
            values.append(field_value)            
        

        values.append(id_tg)
        
        set_clause = ", ".join(set_parts)
        sql = f"UPDATE users SET {set_clause} WHERE id_tg = ?"
        
        await conn.execute(sql, values)
        await conn.commit()
    
    return True