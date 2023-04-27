import betterlogging as logging
from aiogram.fsm.storage.redis import RedisStorage
from aiogram import Bot, Dispatcher


from config import hidden_vars

logging.basic_colorized_config(level=logging.DEBUG,
                               format="%(asctime)s - [%(levelname)s] - %(name)s - "
                                      "(%(filename)s).%funcName)s(%(lineno)d) - %(message)s"
                               )
storage = RedisStorage.from_url('redis://@localhost:6379/0')
bot = Bot(token=hidden_vars.tg_bot.bot_token)
dp = Dispatcher()
