from aiogram.types import BotCommand

commands = [
    BotCommand(
        command='start',
        description='Начало работы бота'
    ),
    BotCommand(
        command='addpost',
        description='Предложить ПОСТ'
    ),
    BotCommand(
        command='admin',
        description='Пишем сообщению АДМИНУ'
    )
]
