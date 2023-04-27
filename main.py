import asyncio
import logging

from autoposting_vk.core import start_autopost
from bot import dp, bot, storage
from commands import commands
from handlers.admin import register_admin_handlers, admin_router_
from handlers.user import register_user_handlers, user_router_
from middleware.albummiddleware import MediaGroupMiddleware
from middleware.throttlingmiddleware import ThrottlingMiddleware


async def bot_working():
    dp.message.middleware.register(ThrottlingMiddleware(storage=storage))
    user_router_.message.middleware(MediaGroupMiddleware())
    register_admin_handlers()
    register_user_handlers()
    dp.include_routers(admin_router_, user_router_, )
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(commands)
    try:
        await dp.start_polling(bot)
    except Exception as ex:
        logging.error(f"[!!! Exception] - {ex}", exc_info=True)
    finally:
        await bot.session.close()
        await dp.storage.close()


async def main():
    bot_task = asyncio.create_task(bot_working())
    auto_posting_task = asyncio.create_task(start_autopost())
    await asyncio.gather(bot_task, auto_posting_task)


if __name__ == "__main__":
    asyncio.run(main())
