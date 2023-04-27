import asyncio
import json
import string

from typing import List

from aiogram.filters import CommandStart, Command, Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import \
    Message, \
    CallbackQuery, \
    InputMedia, \
    ContentType as CT

from aiogram import F, Router

from bot import bot
from core_func import date_out
from bot_db_work import write_db
from config import hidden_vars
from keyboards.user_kb import cancel_kb, add_media_ikb, published_ikb

user_router_ = Router()


class DownloadData(StatesGroup):
    admin_text = State()
    post_caption = State()
    add_media = State()


async def command_start(m: Message):
    write_db(date_out(m.date),
             m.from_user.id,
             m.from_user.first_name,
             m.from_user.last_name,
             m.from_user.username,
             m.message_id)
    sign = str(m.from_user.full_name)
    text = f'Привет, {sign}. Тут всё очень просто:)\nВнизу слева есть меню команд'
    await m.answer_photo(photo='AgACAgIAAxkBAAITZmQlo77a9vGGy1DlE30EBC652E9-AAIyxjEbbWMpSZgCRTKnxt4VAQADAgADeQADLwQ',
                         caption=text)
    await asyncio.sleep(2)
    await m.answer('↓ ↓ ↓')


async def to_admin(m: Message, state: FSMContext):
    await m.answer('АДМИН этого канала готов выслушать все предложения и пожелания')
    await state.set_state(DownloadData.admin_text)


async def send_admin(m: Message, state: FSMContext):
    header = f"---Сообщение Админу---\n" \
             f"Отправитель: {m.from_user.id}\n" \
             f"{m.from_user.full_name}\n" \
             f"username is empty" \
             f"\nСообщение:\n"
    header = header.replace('username is empty', '@' + m.from_user.username) if m.from_user.username else header
    text = header + m.text
    await bot.send_message(chat_id=hidden_vars.tg_bot.admin_id[0],
                           text=text)
    await state.clear()
    await m.reply('Сообщение админу отправлено, он уже читает его')
    await asyncio.sleep(1)
    await m.answer('Кстати, ответить он на него не может, '
                   'но если увидит в вашем послании что-то ценное, то обязательно свяжется :)')
    await asyncio.sleep(2)
    await m.answer('Желаю всего наилучшего')


async def start_post(m: Message, state: FSMContext):
    await m.answer('Что бы у нас всё получилось, будь очень внимателен и следуй моим подсказкам\n'
                   'читай подсказки - ЭТО ВАЖНО')

    await asyncio.sleep(2)
    await m.answer('Пост или новость (называй, как хочешь) можно предложить, как просто в виде текста, '
                   'так и с медиафайлом. Это может быть одно или несколько ФОТО или ВИДЕО. Так же '
                   'можно добавлять и документы.')
    await asyncio.sleep(2)
    await m.answer('Сначала тебе необходимо написать текст новости и нажимай отправить\n\n'
                   'Не забудь указать номер телефона или другой контакт, если это необходимо\n\n'
                   'Жду пока ты напишешь и отправишь текст')
    await state.set_state(DownloadData.post_caption)


async def get_text(m: Message, state: FSMContext):
    received_message = f'{m.text}\n\n{m.from_user.full_name}'
    received_message = received_message + '\n@' + m.from_user.username if m.from_user.username else received_message
    await state.update_data(post_caption=received_message)
    await m.answer(text='Текст твоего поста будет выглядить так:\n\n' + received_message)
    await asyncio.sleep(1)
    await m.answer('Пост не содержит медиафайл. Как поступим?', reply_markup=add_media_ikb.as_markup())


async def choose_media(cb: CallbackQuery, state=FSMContext):
    await cb.message.answer('Добавьте медиа файлы. Подпись к файлам добавлять НЕ нужно', reply_markup=cancel_kb)
    await state.set_state(state=DownloadData.add_media)


async def send_without_media(cb: CallbackQuery, state=FSMContext):
    result = await state.get_data()
    text = result.get('post_caption')
    text = f"{text}\n @{cb.from_user.username}" if cb.from_user.username else text
    header = f"---Предложен пост---\n" \
             f"Отправитель: {cb.from_user.id}\n" \
             f"{cb.from_user.full_name}\n" \
             f"username is empty" \
             f"\n- - -"
    header = header.replace("username is empty", '@' + cb.from_user.username) if cb.from_user.username else header
    await bot.send_message(chat_id=hidden_vars.tg_bot.admin_id[0], text=header)
    await bot.send_message(chat_id=hidden_vars.tg_bot.admin_id[0], text=text)
    await state.clear()


async def handle_one_media(m: Message, state: FSMContext):
    caption = await state.get_data()
    media_file: List = list()
    type_att = m.content_type
    if type_att == 'photo':
        file_id = m.photo[-1].file_id
    else:
        file_id = m.dict()[type_att].get("file_id")
    media_file.append(InputMedia(media=file_id,
                                 type=m.content_type,
                                 caption=caption.get('post_caption')))
    await state.update_data(add_media=media_file)
    await m.answer('Теперь пост будет таким')
    await m.answer_media_group(media_file)
    await m.answer("Публикуем?", reply_markup=published_ikb.as_markup())


async def handle_albums(m: Message, album: list[Message], state: FSMContext):
    caption = await state.get_data()
    media_group: List = list()
    for msg in album:
        if msg.photo:
            file_id = msg.photo[-1].file_id
        else:
            obj_dict = msg.dict()
            file_id = obj_dict[msg.content_type]['file_id']
        try:
            if msg == album[0]:
                media_group.append(InputMedia(media=file_id,
                                              type=msg.content_type,
                                              caption=caption.get('post_caption')))
            else:
                media_group.append(InputMedia(media=file_id,
                                              type=msg.content_type))
        except ValueError:
            return await m.answer("This type of album is not supported")
    await state.update_data(add_media=media_group)
    await m.answer('Теперь пост будет таким')
    await m.answer_media_group(media_group)
    await m.answer("Публикуем?", reply_markup=published_ikb.as_markup())


async def published_with_media(cb: CallbackQuery, state: FSMContext):
    result = await state.get_data()
    header = f"---Предложен пост---\n" \
             f"Отправитель: {cb.from_user.id}\n" \
             f"{cb.from_user.full_name}\n" \
             f"username is empty" \
             f"\n- - -"
    header = header.replace("username is empty", '@' + cb.from_user.username) if cb.from_user.username else header
    await bot.send_message(chat_id=hidden_vars.tg_bot.admin_id[0], text=header)
    await bot.send_media_group(chat_id=hidden_vars.tg_bot.admin_id[0], media=result.get('add_media'))
    await cb.message.answer('Пост отправлен')
    await state.clear()


async def cancel(m: Message, state: FSMContext):
    await m.delete()
    await m.answer('Действия отменены, нужно начинать заново')
    await m.answer('Пользуйся командами')
    await m.answer('↓ ↓ ↓')
    await state.clear()


async def echo(m: Message):
    if {i.lower().translate(str.maketrans('', '', string.punctuation)) for i in m.text.split(' ')} \
            .intersection(set(json.load(open('very_bad_word.json')))):
        await m.delete()
    else:
        await bot.send_message(chat_id=hidden_vars.tg_bot.admin_id[0],
                               text=f'Сработал Echo в Lenino Public\n'
                                    f'{m.from_user.username} {m.from_user.full_name}\n'
                                    f'---------\n'
                                    f'{m.text}')
        await m.reply('Я понимаю о чем ты, но общаться могу только через команды меню')


def register_user_handlers():
    user_router_.message.register(command_start, CommandStart())
    user_router_.message.register(to_admin, Command('admin'))
    user_router_.message.register(send_admin, DownloadData.admin_text)
    user_router_.message.register(start_post, Command('addpost'))
    user_router_.message.register(get_text, DownloadData.post_caption)
    user_router_.callback_query.register(choose_media, Text('add_media'))
    user_router_.callback_query.register(send_without_media, Text('post_without_media'))
    user_router_.message.register(cancel, F.text == 'Отмена действий')
    user_router_.message.register(handle_albums,
                                  DownloadData.add_media, F.media_group_id)
    user_router_.message.register(handle_one_media,
                                  DownloadData.add_media,
                                  F.content_type.in_([CT.PHOTO, CT.VIDEO, CT.AUDIO, CT.DOCUMENT]))
    user_router_.callback_query.register(published_with_media, Text('published_with_media'))
    user_router_.message.register(echo, F.text)
