import os
import aiosqlite
from logs.logger import logger
from db.users_crud import get_user_stats
from db.database import create_table

async def send_admin_stats(application):
    """Отправляет статистику админу при запуске бота И логирует в файл"""
    try:
        admin_id = int(os.getenv("ADMIN_ID"))
        total_users, tag_stats = await get_user_stats()
        
        # Получаем количества по тегам
        hot_count = tag_stats.get('Горячий', 0)
        normal_count = tag_stats.get('Обычный', 0) 
        cold_count = tag_stats.get('Холодный', 0)
        
        # Формируем сообщение для админа
        message = "📊 *Статистика при запуске бота:*\n\n"
        message += f"👥 Всего пользователей: {total_users}\n\n"
        message += "📈 Распределение по тегам:\n"
        message += f"🔥 Горячих: {hot_count}\n"
        message += f"⚡ Обычных: {normal_count}\n" 
        message += f"❄️ Холодных: {cold_count}\n"
        
        # ✅ 1. ЛОГИРУЕМ В ЧАТ (в файл логов)
        logger.info(f"📊 Статистика бота: всего пользователей {total_users}, "
                   f"горячих {hot_count}, обычных {normal_count}, холодных {cold_count}")
        
        # ✅ 2. ОТПРАВЛЯЕМ АДМИНУ (в Telegram)
        await application.bot.send_message(
            chat_id=admin_id,
            text=message,
            parse_mode="Markdown"
        )
        
        logger.info("✅ Статистика отправлена админу и записана в лог")
        
    except Exception as e:
        logger.error(f"❌ Ошибка отправки статистики: {e}")

async def post_init(application):
    """Функция, которая запускается после инициализации бота"""
    await create_table(application)
    await send_admin_stats(application)