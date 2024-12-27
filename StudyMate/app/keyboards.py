from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                          InlineKeyboardMarkup, InlineKeyboardButton)

markup = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Личный кабинет")],
        [KeyboardButton(text="Список задач")],
        [KeyboardButton(text="Добавить задачу")]
    ],
    resize_keyboard=True,
    input_field_placeholder='Выберите пункт меню...'
)

get_number = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Отправить номер', request_contact=True)]
    ],
    resize_keyboard=True
)

profile = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Пройти регистрацию еще раз', callback_data='reregister')]
    ]
)

