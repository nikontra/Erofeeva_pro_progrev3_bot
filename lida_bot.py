import lida_bot_texts
import os
# from subprocess import Popen, PIPE
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update, Bot
from telegram.ext import (Updater,
                          CommandHandler,
                          MessageHandler,
                          CallbackQueryHandler,
                          Filters,
                          ConversationHandler,
                          CallbackContext,)
from telegram.utils.request import Request
from dotenv import load_dotenv

from db import init_db, add_user, list_user, clear_user
from buttons import get_base_reply_keyboard, BUTTON1_LIST, BUTTON2_CLEAR

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
OWNER_ID = os.getenv('OWNER_ID')
TIMEOUT = 300

CALLBACK_BUTTON1_READY = "callback_button1_ready"
CALLBACK_BUTTON2_YES = "callback_button2_yes"
CALLBACK_BUTTON3_LESSON1 = "callback_button3_lesson1"
CALLBACK_BUTTON4_CONTACT = "callback_button4_contact"
CALLBACK_BUTTON5_YES = "callback_button5_yes"
CALLBACK_BUTTON5_NO = "callback_button5_no"

TITLES = {
    CALLBACK_BUTTON1_READY: "Готов",
    CALLBACK_BUTTON2_YES: "Договорились",
    CALLBACK_BUTTON3_LESSON1: "Посмотреть урок",
    CALLBACK_BUTTON4_CONTACT: "Хочу разбор",
    CALLBACK_BUTTON5_YES: "Да",
    CALLBACK_BUTTON5_NO: "Ещё нет",
}

READY, YES, NAME, EMAIL, LESSON, GIFT = range(6)
URL1 = 'https://clck.ru/32DUSp'
URL2 = 'https://clck.ru/32MsSA'
ACCOUNT = 'https://t.me/LidiaErofeeva'


def get_inline_keyboard_one_key(text, callback_data=None, url=None):
    """Клавиатура с одной кнопкой"""
    keyboard = [
        [
            InlineKeyboardButton(text=text, callback_data=callback_data, url=url),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_inline_keyboard_two_key(text1, callback_data1, text2, callback_data2):
    """Клавиатура с двумя кнопками"""
    keyboard = [
        [
            InlineKeyboardButton(text=text1, callback_data=callback_data1),
            InlineKeyboardButton(text=text2, callback_data=callback_data2),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def time_message_1(context: CallbackContext):
    """Выполняет задание - отправляет сообщение"""
    context.bot.send_message(
        chat_id=context.job.context,
        text=lida_bot_texts.TEXT7_TIME_MESSAGE,
        reply_markup=get_inline_keyboard_two_key(
            text1=TITLES[CALLBACK_BUTTON5_YES],
            callback_data1=CALLBACK_BUTTON5_YES,
            text2=TITLES[CALLBACK_BUTTON5_NO],
            callback_data2=CALLBACK_BUTTON5_NO,
        ),
    )


def time_message_2(context: CallbackContext):
    """Выполняет задание - отправляет сообщение"""
    context.bot.send_message(
        chat_id=context.job.context,
        text=lida_bot_texts.TEXT9_FINAL_MESSAGE,
        reply_markup=get_inline_keyboard_one_key(
            text=TITLES[CALLBACK_BUTTON4_CONTACT],
            url=ACCOUNT,
        ),
    )


def job_time_message(context, chat_id, timer):
    """Создает задание - отправить сообщение через временной интервал"""
    timeout = TIMEOUT
    job = context.job_queue.run_once(
        callback=time_message_1 if timer == 1 else time_message_2,
        when=timeout,
        context=chat_id,
    )
    context.chat_data['job'] = job


def do_list_users(update: Update, context: CallbackContext):
    """Список пользователей оставивших контакты"""
    users = list_user()
    text = '\n'.join(
        [f'{user_username} - {user_email} - {user_tell}' for user_username, user_email, user_tell in users]
    )
    update.effective_message.reply_text(
        text=text,
    )


def do_clear_users(update: Update, context: CallbackContext):
    """Очистить список пользователей"""
    clear_user()
    text = 'Список контактов успешно очищен'
    update.effective_message.reply_text(
        text=text,
    )


def do_echo(update: Update, context: CallbackContext):
    """Обработка кнопок админки"""
    text = update.message.text
    chat_id = update.effective_chat.id
    if text == BUTTON1_LIST and chat_id == OWNER_ID:
        return do_list_users(update=update, context=context)
    elif text == BUTTON2_CLEAR and chat_id == OWNER_ID:
        return do_clear_users(update=update, context=context)


def do_start(update: Update, context: CallbackContext):
    """Старт диалога, для Админа - админка"""
    chat_id = update.effective_chat.id
    if chat_id == OWNER_ID:
        context.bot.send_message(
            chat_id=OWNER_ID,
            text='Привет',
            reply_markup=get_base_reply_keyboard()
        )
    else:
        context.bot.send_message(
            chat_id=chat_id,
            text=lida_bot_texts.TEXT1_HI,
            reply_markup=get_inline_keyboard_one_key(
                text=TITLES[CALLBACK_BUTTON1_READY],
                callback_data=CALLBACK_BUTTON1_READY
            )
        )


def keyboard_callback_handler(update: Update, context: CallbackContext):
    """Обработка кнопок inline-клавиатуры"""
    query = update.callback_query
    data = query.data
    chat_id = update.effective_message.chat_id
    # current_text = update.effective_message.text
    if data == CALLBACK_BUTTON1_READY:
        context.bot.send_message(
            chat_id=chat_id,
            text=lida_bot_texts.TEXT2_WANT,
            reply_markup=get_inline_keyboard_one_key(
                text=TITLES[CALLBACK_BUTTON2_YES],
                callback_data=CALLBACK_BUTTON2_YES
            )
        )
        return YES
    elif data == CALLBACK_BUTTON2_YES:
        context.bot.send_message(
            chat_id=chat_id,
            text=lida_bot_texts.TEXT3_NAME,
        )
        return NAME
    elif data == CALLBACK_BUTTON5_YES:
        text = lida_bot_texts.TEXT8_YES_GIFT
        context.bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=get_inline_keyboard_one_key(
                text=TITLES[CALLBACK_BUTTON3_LESSON1],
                url=URL2,
            ),
        )
        job_time_message(
            context=context,
            chat_id=update.effective_chat.id,
            timer=2
        )
        return ConversationHandler.END
    elif data == CALLBACK_BUTTON5_NO:
        text = lida_bot_texts.TEXT8_NO_GIFT
        context.bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=get_inline_keyboard_one_key(
                text=TITLES[CALLBACK_BUTTON3_LESSON1],
                url=URL2,
            ),
        )
        job_time_message(
            context=context,
            chat_id=update.effective_chat.id,
            timer=2
        )
        return ConversationHandler.END
    


def name_handler(update: Update, context: CallbackContext):
    """Получает имя пользователя"""
    context.user_data[NAME] = update.message.text
    text = f'{context.user_data[NAME]} {lida_bot_texts.TEXT4_EMAIL}'
    update.message.reply_text(
        text=text,
    )
    return EMAIL


def email_handler(update: Update, context: CallbackContext):
    """Получает почту пользователя"""
    context.user_data[EMAIL] = update.message.text
    add_user(
        username=context.user_data[NAME],
        email=context.user_data[EMAIL],
    )
    text = lida_bot_texts.TEXT6_LESSON_1
    update.message.reply_text(
        text=text,
        reply_markup=get_inline_keyboard_one_key(
            text=TITLES[CALLBACK_BUTTON3_LESSON1],
            url=URL1,
        ),
    ),
    job_time_message(
        context=context,
        chat_id=update.effective_chat.id,
        timer=1
    )
    return GIFT
    

def cancel_handler(update: Update, context: CallbackContext):
    """ Отменить весь процесс диалога. Данные будут утеряны"""
    update.message.reply_text('Отмена. Для начала с нуля нажмите /start')
    return ConversationHandler.END


def main():
    req = Request(
        connect_timeout=0.5,
        read_timeout=1.0,
    )
    bot = Bot(
        token=TELEGRAM_TOKEN,
        request=req,
    )
    updater = Updater(
        bot=bot,
        use_context=True,
    )
    init_db()
    conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(callback=keyboard_callback_handler, pass_user_data=True),
        ],
        states={
            YES: [
                CallbackQueryHandler(keyboard_callback_handler, pass_user_data=True),
            ],
            NAME: [
                MessageHandler(Filters.all, name_handler, pass_user_data=True),
            ],
            EMAIL: [
                MessageHandler(Filters.all, email_handler, pass_user_data=True),
            ],
            GIFT: [
                CallbackQueryHandler(keyboard_callback_handler, pass_user_data=True),
            ],
        },
        fallbacks=[
            CommandHandler('cancel', cancel_handler),
        ],
    )
    start_handler = CommandHandler('start', do_start)
    message_handler = MessageHandler(Filters.text, do_echo)

    updater.dispatcher.add_handler(start_handler)
    updater.dispatcher.add_handler(conv_handler)
    updater.dispatcher.add_handler(message_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
