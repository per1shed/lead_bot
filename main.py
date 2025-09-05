import logging
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, 
    ContextTypes, 
    CommandHandler, 
    ConversationHandler, 
    MessageHandler,
    filters
)

load_dotenv()       # ищет переменные, которые написали и экспортирует их в виртуальное окружение
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


FIRST_MESSAGE, GET_NAME = range(2)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # update - полная информация о том что произошло
    # update.effective_user - информация о человеке
    # update.effective_chat - информация о чате
    # update.effective_message - информация о сообщении
    # context - контекст, в котром мы можем использовать бота

    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text=f"Привет, {update.effective_user.first_name}. Хочешь гайд?",
    )
    return FIRST_MESSAGE

async def get_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    answer = update.effective_message.text
    if answer == 'Да':
        await context.bot.send_message(
        chat_id=update.effective_user.id,
        text=f"Чтобы забрать гайд, напиши свое имя",
    )


if __name__ == '__main__':
    application = (
        ApplicationBuilder()
        .token(os.getenv("TOKEN"))
        .build()
        )
    # Handler - обработчик, который будет обрабатывать
    # CommandHandler - обработчик, который будет обрабатывать команды
    # MessageHandler - обработчки, который будет обрабатывать сообщения
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            FIRST_MESSAGE: [
                MessageHandler(
                    filters=filters.TEXT & filters.COMMAND, 
                    callback=get_answer
                )
            ]
        }, 
        fallbacks=[CommandHandler("start", start)]
    )



    application.add_handler(conv_handler)
    
    application.run_polling()