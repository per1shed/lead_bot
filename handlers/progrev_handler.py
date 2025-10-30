from datetime import timedelta
import os

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
)


from config.states import (
    FIRST_MESSAGE,
    GET_NAME,
    GET_PHONE,
    GET_EMAIL,
    GET_CONSENT,
    INLINE_BUTTON,
)
from utils.escape_sym import escape_sym
from handlers.jobs import reminder
from db.users_crude import create_user, get_user, update_user



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # update - полная информация о том что произошло
    # update.effective_user - информация о человеке
    # update.effective_chat - информация о чате
    # update.effective_message - информация о сообщении
    # context - контекст, в котором мы можем использовать бота

    query = update.callback_query
    """отвечаем на кнопку InlineKeyboardButton"""
    if query:
        await query.answer()
        await query.delete_message()
    else:
        if not await get_user(update.effective_user.id):
            await create_user(update.effective_user.id)

    """отправляем сообщение с кнопками"""
    keyboard = [["Да", "Нет"], ["Еще не знаю"]]
    markup = ReplyKeyboardMarkup(
        keyboard,
        one_time_keyboard=True,
        input_field_placeholder="Выбери вариант ответа",
    )
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text=escape_sym(f"Привет, {update.effective_user.first_name}.\n*Хочешь гайд?*"),
        reply_markup=markup,
        parse_mode="MarkdownV2",
    )
    job = context.job_queue.run_once(
        reminder,
        when=timedelta(minutes=60), data={"message": "Вы остановились на половине пути. Для того, чтобы забрать подарок ответьте на оставшиеся вопросы."},
        name="reminder",
        chat_id=update.effective_user.id,
    )
    context.user_data['job'] = job
    return FIRST_MESSAGE


async def get_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['job'].schedule_removal()
    answer = update.effective_message.text
    context.user_data["answer"] = answer
    # Достать значение, которое было положено в словарь можно следующим образом:
    # print(context.user_data['answer'])
    keyboard = [[update.effective_user.first_name]]
    markup = ReplyKeyboardMarkup(
        keyboard,
        one_time_keyboard=True,
        input_field_placeholder="Нажмите на свое имя или напишите его",
    )
    job_answer = context.job_queue.run_once(
        reminder,
        when=timedelta(minutes=60),
        data={"message": "Вы остановились на половине пути. Для того, чтобы забрать подарок ответьте на оставшиеся вопросы."},
        name="reminder",
        chat_id=update.effective_user.id,
    )
    context.user_data['job_answer'] = job_answer
    if answer.lower() in ["да", "yes"]:
        await context.bot.send_message(
            chat_id=update.effective_user.id, text="Как вас зовут?", reply_markup=markup
        )
        return GET_NAME
    else:
        keyboard = [
            [
                InlineKeyboardButton("Да", callback_data="yes"),
                InlineKeyboardButton("Нет", callback_data="no"),
            ]
        ]
        markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(
            chat_id=update.effective_user.id, text="Тогда все!", reply_markup=markup
        )
        return INLINE_BUTTON


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_message.text

    await update_user(update.effective_user.id, name=name)
    
    context.user_data['job_answer'].schedule_removal()
    context.user_data["name"] = name
    keyboard = [[KeyboardButton("Отправить номер телфона", request_contact=True)]]
    markup = ReplyKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text="Отлично! Теперь напиши свой номер телефона.",
        reply_markup=markup,
    )
    job_name = context.job_queue.run_once(
        reminder,
        when=timedelta(minutes=60),
        data={"message": "Вы остановились на половине пути. Для того, чтобы забрать подарок ответьте на оставшиеся вопросы."},
        name="reminder",
        chat_id=update.effective_user.id,
    )
    context.user_data['job_name'] = job_name
    return GET_PHONE


async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['job_name'].schedule_removal()
    phone = update.effective_message.contact.phone_number
    context.user_data["phone"] = phone

    await update_user(update.effective_user.id, phone=phone)

    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text="Супер! Теперь напиши свою электронную почту.",
    )
    job_phone = context.job_queue.run_once(
        reminder,
        when=timedelta(minutes=60),
        data={"message": "Вы остановились на половине пути. Для того, чтобы забрать подарок ответьте на оставшиеся вопросы."},
        name="reminder",
        chat_id=update.effective_user.id,
    )
    context.user_data['job_phone'] = job_phone
    return GET_EMAIL


async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['job_phone'].schedule_removal()
    email = update.effective_message.text
    context.user_data["email"] = email

    await update_user(update.effective_user.id, email=email)

    keyboard = [
        [
            InlineKeyboardButton("Да, согласен", callback_data="consent_yes"),
            InlineKeyboardButton("Нет, не согласен", callback_data="consent_no"),
        ]
    ]
    markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text="Согласны ли вы на обработку персональных данных?",
        reply_markup=markup,
    )
    job_mail = context.job_queue.run_once(
        reminder,
        when=timedelta(minutes=60),
        data={"message": "Вы остановились на половине пути. Для того, чтобы забрать подарок ответьте на оставшиеся вопросы."},
        name="reminder",
        chat_id=update.effective_user.id,
    )
    context.user_data['job_mail'] = job_mail
    return GET_CONSENT


async def get_consent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['job_mail'].schedule_removal()
    query = update.callback_query
    await query.answer()

    admin_id = int(os.getenv("ADMIN_ID"))

    if query.data == "consent_yes":
        name = context.user_data.get("name", "пользователь")
        phone = context.user_data.get("phone", "не указан")
        email = context.user_data.get("email", "не указан")

        await update_user(update.effective_user.id, agreement=1)

        await context.bot.send_message(
            chat_id=admin_id,
            text="Новая заявка!\n\n"
            f"Имя: {name}\n"
            f"Телефон: {phone}\n"
            f"Email: {email}\n"
            f"ID пользователя: {update.effective_user.id}",
        )

        keyboard = [
            [
                InlineKeyboardButton(
                    "Восстановление",
                    url="https://moments-smell-kd7.craft.me/tloxRtR4yzlh28",
                )
            ],
            [
                InlineKeyboardButton(
                    "Программа тренировок",
                    url="https://moments-smell-kd7.craft.me/A4iE8g5YL1dbkp",
                )
            ],
        ]
        markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text="Отлично! Теперь выберите подарок, который хотите получить:",
            reply_markup=markup,
        )
        context.user_data.clear()
        return ConversationHandler.END
    else:
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text="Без согласия на обработку данных мы не можем отправить программу тренировок. Для того, чтобы начать заново - нажмите /start",
        )
        context.user_data.clear()
        return FIRST_MESSAGE


async def get_inline_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("спасибо за ответ!", show_alert=True)
    if query.data == "yes":
        keyboard = [[InlineKeyboardButton("Да", callback_data="yes")]]
        markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="спасибо за ответ!", reply_markup=markup)
