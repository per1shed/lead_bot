import logging
import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

load_dotenv()
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)

FIRST_MESSAGE, GET_NAME, GET_PHONE, GET_EMAIL, GET_CONSENT = range(5)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text=f"Привет, {update.effective_user.first_name}. Хочешь гайд?",
    )
    return FIRST_MESSAGE

async def get_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    answer = update.effective_message.text
    if answer.lower() in ["да", "yes"]:
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text="Как вас зовут?",
        )
        return GET_NAME
    else:
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text="Жаль! Если передумаешь - напиши /start",
        )
        return FIRST_MESSAGE

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.effective_message.text
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text="Отлично! Теперь напиши свой номер телефона.",
    )
    return GET_PHONE

async def get_tel_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['phone'] = update.effective_message.text
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text="Супер! Теперь напиши свою электронную почту.",
    )
    return GET_EMAIL

async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['email'] = update.effective_message.text
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text="Согласны ли вы на обработку персональных данных? (Да/Нет)",
    )
    return GET_CONSENT

async def get_consent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await send_training_program(update, context)

async def send_training_program(update: Update, context: ContextTypes.DEFAULT_TYPE):
    consent = update.effective_message.text.lower()

    if consent in ['да', 'yes', 'согласен', 'согласна']:
        name = context.user_data.get('name', 'пользователь')
        phone = context.user_data.get('phone', 'не указан')
        email = context.user_data.get('email', 'не указан')

        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text=f"Отлично, {name}! Вот ваша программа тренировок:\n\n"
                 "Программа на неделю:\n"
                 "Понедельник: Грудь + Трицепс\n"
                 "Вторник: Спина + Бицепс\n"
                 "Среда: Отдых\n"
                 "Четверг: Ноги + Плечи\n"
                 "Пятница: Кардио + Пресс\n"
                 "Суббота: Отдых\n"
                 "Воскресенье: Активный отдых\n\n"
                 f"Ваши данные:\n"
                 f"Имя: {name}\n"
                 f"Телефон: {phone}\n"
                 f"Email: {email}"
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text="Без согласия на обработку данных мы не можем отправить программу тренировок."
        )
    
    context.user_data.clear()
    return ConversationHandler.END

if __name__ == "__main__":
    application = ApplicationBuilder().token(os.getenv("TOKEN")).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            FIRST_MESSAGE: [
                MessageHandler(
                    filters=filters.TEXT & ~filters.COMMAND, callback=get_answer)
            ],
            GET_NAME: [
                MessageHandler(
                    filters=filters.TEXT & ~filters.COMMAND, callback=get_name)
            ],
            GET_PHONE: [
                MessageHandler(
                    filters=filters.TEXT & ~filters.COMMAND, callback=get_tel_number)
            ],
            GET_EMAIL: [
                MessageHandler(filters=filters.TEXT & ~filters.COMMAND, callback=get_email)
            ],
            GET_CONSENT: [
                MessageHandler(
                    filters=filters.TEXT & ~filters.COMMAND, callback=get_consent)
            ]
        },
        fallbacks=[CommandHandler("start", start)],
    )

    application.add_handler(conv_handler)
    application.run_polling()