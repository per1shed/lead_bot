from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from db.users_crud import get_users
from logs.logger import logger
from config.states import ADMIN_START
import csv
import asyncio
import aiosqlite


async def admins_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Список пользовтаелй", callback_data="user_list")],
        [
            InlineKeyboardButton(
                "Список пользователей с тегом Горячий", callback_data="hot_user_list"
            )
        ],
        [
            InlineKeyboardButton(
                "Список пользователей с тегом Обычный", callback_data="usual_user_list"
            )
        ],
        [
            InlineKeyboardButton(
                "Список пользователей с тегом Холодный", callback_data="cold_user_list"
            )
        ],
        [
            InlineKeyboardButton(
                "Список пользователей csv", callback_data="csv_users_list"
            )
        ],
        [InlineKeyboardButton("Рассылка", callback_data="send_message")],
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text="Привет, админ!",
        reply_markup=markup,
    )
    return ADMIN_START


async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = await get_users()
    text = "Список пользователй:\n"
    text += "№ \\- ссылка \\- телефон  \\- email\\n"
    for n, user in enumerate(users, 1):
        text += (
            f"{n}\\.[{user[2]}](tg://user?id={user[1]}) \\- {user[3]} \\- {user[4]}\n"
        )
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text=text,
        parse_mode="MarkdownV2",
    )
    return await admins_start(update, context)


async def csv_users_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = await get_users()
    with open("users.csv", "w", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["№", "ссылка", "телефон", "email"])
        for n, user in enumerate(users, 1):
            writer.writerow([n, user[2], user[3], user[4]])

    await context.bot.send_document(
        chat_id=update.effective_user.id,
        document=open("users.csv", "rb"),
        caption="список пользователй csv",
    )
    await admins_start(update, context)


async def spam_send_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Простейшая рассылка: админ пишет текст, бот сразу рассылает
    """
    query = update.callback_query
    await query.answer()
    
    # Просто отправляем сообщение
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text="✍️ *Отправьте текст для рассылки*\n\n"
             "Следующее ваше текстовое сообщение будет разослано ВСЕМ пользователям\\.",
        parse_mode="MarkdownV2"
    )
    
    # Запоминаем, что следующее сообщение админа - текст рассылки
    # Просто записываем в user_data
    context.user_data['next_message_is_broadcast'] = True


# И добавляем обработчик ВСЕХ сообщений админа:
async def handle_all_admin_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обрабатывает все текстовые сообщения админа
    """
    # Проверяем, не является ли это командой
    if update.message and update.message.text:
        # Если это текст рассылки
        if context.user_data.get('next_message_is_broadcast'):
            # Убираем флаг
            context.user_data.pop('next_message_is_broadcast', None)
            
            # Получаем текст
            message_text = update.message.text
            
            # Немедленно начинаем рассылку
            users = await get_users()
            
            await update.message.reply_text(f"📤 Рассылаю сообщение {len(users)} пользователям...")
            
            success = 0
            for user in users:
                try:
                    await context.bot.send_message(
                        chat_id=user[1],
                        text=message_text
                    )
                    success += 1
                except:
                    pass
            
            await update.message.reply_text(f"✅ Готово! Отправлено {success} пользователям.")
            
            # Возвращаем меню
            return await admins_start(update, context)
    
    # Если не текст рассылки, показываем меню
    return await admins_start(update, context)


async def get_users_by_tag(tag_name: str):
    """Получить пользователей с определенным тегом"""
    async with aiosqlite.connect('lead.db') as conn:
        cursor = await conn.execute('''
            SELECT u.id, u.id_tg, u.name, u.phone, u.email, u.created_at
            FROM users u
            JOIN user_tags ut ON u.id = ut.user_id
            JOIN tags t ON ut.tag_id = t.id
            WHERE t.name = ?
            ORDER BY u.created_at DESC
        ''', (tag_name,))
        return await cursor.fetchall()
    

async def show_hot_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать пользователей с тегом 'Горячий'"""
    query = update.callback_query
    await query.answer()
    
    users = await get_users_by_tag("Горячий")
    
    if not users:
        await query.edit_message_text("🔥 *Пользователи с тегом 'Горячий':*\n\n📭 Нет пользователей")
        return await admins_start(update, context)
    
    text = "🔥 *Пользователи с тегом 'Горячий':*\n\n"
    text += "№ \\- имя \\- телефон \\- email \\- дата\n"
    
    for n, user in enumerate(users, 1):
        name = user[2] or "Без имени"
        phone = user[3] or "Нет телефона"
        email = user[4] or "Нет email"
        date = user[5][:10] if user[5] else "Нет даты"
        
        text += f"{n}\\. [{name}](tg://user?id={user[1]}) \\- {phone} \\- {email} \\- {date}\n"
    
    await query.edit_message_text(
        text=text,
        parse_mode="MarkdownV2"
    )
    
    # Возвращаемся в меню
    await admins_start(update, context)


async def show_usual_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать пользователей с тегом 'Обычный'"""
    query = update.callback_query
    await query.answer()
    
    users = await get_users_by_tag("Обычный")
    
    if not users:
        await query.edit_message_text("⚡ *Пользователи с тегом 'Обычный':*\n\n📭 Нет пользователей")
        return await admins_start(update, context)
    
    text = "⚡ *Пользователи с тегом 'Обычный':*\n\n"
    text += "№ \\- имя \\- телефон \\- email \\- дата\n"
    
    for n, user in enumerate(users, 1):
        name = user[2] or "Без имени"
        phone = user[3] or "Нет телефона"
        email = user[4] or "Нет email"
        date = user[5][:10] if user[5] else "Нет даты"
        
        text += f"{n}\\. [{name}](tg://user?id={user[1]}) \\- {phone} \\- {email} \\- {date}\n"
    
    await query.edit_message_text(
        text=text,
        parse_mode="MarkdownV2"
    )
    
    await admins_start(update, context)


async def show_cold_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать пользователей с тегом 'Холодный'"""
    query = update.callback_query
    await query.answer()
    
    users = await get_users_by_tag("Холодный")
    
    if not users:
        await query.edit_message_text("❄️ *Пользователи с тегом 'Холодный':*\n\n📭 Нет пользователей")
        return await admins_start(update, context)
    
    text = "❄️ *Пользователи с тегом 'Холодный':*\n\n"
    text += "№ \\- имя \\- телефон \\- email \\- дата\n"
    
    for n, user in enumerate(users, 1):
        name = user[2] or "Без имени"
        phone = user[3] or "Нет телефона"
        email = user[4] or "Нет email"
        date = user[5][:10] if user[5] else "Нет даты"
        
        text += f"{n}\\. [{name}](tg://user?id={user[1]}) \\- {phone} \\- {email} \\- {date}\n"
    
    await query.edit_message_text(
        text=text,
        parse_mode="MarkdownV2"
    )
    
    await admins_start(update, context)