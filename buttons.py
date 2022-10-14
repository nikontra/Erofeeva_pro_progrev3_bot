from telegram import KeyboardButton, ReplyKeyboardMarkup


BUTTON1_LIST = 'Список контактов'
BUTTON2_CLEAR = 'Очистить список'


def get_base_reply_keyboard():
    keyboard = [
        [
            KeyboardButton(BUTTON1_LIST),
            KeyboardButton(BUTTON2_CLEAR),
        ],
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )
