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

load_dotenv()
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

from config.states import (
    FIRST_MESSAGE,
    GET_NAME,
    GET_PHONE,
    GET_EMAIL,
    GET_CONSENT,
    INLINE_BUTTON,
)

if __name__ == "__main__":
    application = ApplicationBuilder().token(os.getenv("TOKEN")).build()
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
    )

    application.add_handler(conv_handler)
    application.run_polling()
