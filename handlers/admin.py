from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

from db_func import check_visitors
from filter import AdminFilter
from keyboards.admin_kb import admin_main_kb

admin_router_ = Router()


class AdminState(StatesGroup):
    get_photo = State()


async def cmd_start(m: Message):
    await m.answer('Admin mode', reply_markup=admin_main_kb)


async def choose_photo_download_handler(m: Message, state: FSMContext):
    await m.answer('Добавь фото')
    await state.set_state(AdminState.get_photo)


async def load_get_photo_id(m: Message, state: FSMContext):
    await m.answer(text=f"ID фотографии на сервере Telegram:\n + {str(m.photo[-1].file_id)}")
    await state.clear()


async def show_visitors(m: Message):
    mess = check_visitors()
    await m.answer(mess)


def register_admin_handlers():
    admin_router_.message.filter(AdminFilter())
    admin_router_.message.register(cmd_start, CommandStart())
    admin_router_.message.register(choose_photo_download_handler, F.text == "Загрузить фото в Telegram")
    admin_router_.message.register(load_get_photo_id, AdminState.get_photo)
    admin_router_.message.register(show_visitors, F.text == "Показать 10 последних гостей")
