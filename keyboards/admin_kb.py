from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

admin_main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Показать 10 последних гостей"),
            KeyboardButton(text="Загрузить фото в Telegram")
        ],
    ],
    resize_keyboard=True,
    input_field_placeholder="Ожидаю выбор"
)
