from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

cancel_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Отмена действий"),
        ],
    ],
    resize_keyboard=True)

add_media_ikb = InlineKeyboardBuilder()
add_media_ikb.row(
    InlineKeyboardButton(text="Добавить МЕДИА", callback_data='add_media'),
    InlineKeyboardButton(text="Отправляем так", callback_data='post_without_media'))

published_ikb = InlineKeyboardBuilder()
published_ikb.row(
    InlineKeyboardButton(text="Отправить", callback_data='published_with_media'),
)
