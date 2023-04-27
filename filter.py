from aiogram.filters import BaseFilter
from aiogram.types import Message
from config import hidden_vars


class AdminFilter(BaseFilter):
    is_admin: bool = True

    async def __call__(self, obj: Message):
        return (obj.from_user.id in hidden_vars.tg_bot.admin_id) == self.is_admin
