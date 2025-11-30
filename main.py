import logging
import os

from dotenv import load_dotenv
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
    PicklePersistence,
)

from handlers.progrev_handler import (
    start,
    get_answer,
    get_name,
    get_phone,
    get_email,
    get_consent,
    get_inline_button,
)

from config.states import (
    FIRST_MESSAGE,
    GET_NAME,
    GET_PHONE,
    GET_EMAIL,
    GET_CONSENT,
    INLINE_BUTTON,
)

from db.database import create_table
import asyncio
from logs.logger import logger
from handlers.admin_stats import post_init

load_dotenv()


if __name__ == "__main__":
    persistence = PicklePersistence(filepath="lead_bot")
    application = (
        ApplicationBuilder()
        .token(os.getenv("TOKEN"))
        .persistence(persistence)
        .post_init(post_init)
        .build()
    )
    # Handler - обработчик, который будет обрабатывать
    # CommandHandler - обработчик, котоырй будет обрабатывать команды
    # MessageHandler - обработчик, который будет обрабатвать сообщения
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            FIRST_MESSAGE: [
                MessageHandler(
                    filters=filters.TEXT & ~filters.COMMAND, callback=get_answer
                )
            ],
            GET_NAME: [
                MessageHandler(
                    filters=filters.TEXT & ~filters.COMMAND, callback=get_name
                )
            ],
            GET_PHONE: [
                MessageHandler(
                    filters=filters.CONTACT | filters.TEXT & ~filters.COMMAND,
                    callback=get_phone,
                )
            ],
            GET_EMAIL: [
                MessageHandler(
                    filters=filters.TEXT & ~filters.COMMAND, callback=get_email
                )
            ],
            GET_CONSENT: [
                CallbackQueryHandler(callback=get_consent, pattern="^consent_")
            ],
            INLINE_BUTTON: [
                CallbackQueryHandler(callback=get_inline_button, pattern="yes"),
                CallbackQueryHandler(callback=start, pattern="no"),
            ],
        },
        fallbacks=[CommandHandler("start", start)],
        persistent=True,
        name="conv_handler",
    )

    application.add_handler(conv_handler)
    logger.info("Бот запущен ✅")
    application.run_polling()
