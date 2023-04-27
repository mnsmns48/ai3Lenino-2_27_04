from dataclasses import dataclass
from environs import Env


@dataclass
class TgBot:
    admin_id: list[int]
    tg_chat: int
    bot_token: str
    vk_api_token: str
    vk_token: str
    notification: bool
    owner_id: str
    amount_post_list: int
    request_period: int
    sqlite_db_path: str


@dataclass
class Config:
    tg_bot: TgBot


def load_config(path: str = None):
    env = Env()
    env.read_env()

    return Config(
        tg_bot=TgBot(
            admin_id=list(map(int, env.list("ADMIN"))),
            tg_chat=env.int("CHAT_ID"),
            bot_token=env.str("BOT_TOKEN"),
            vk_api_token=env.str("VK_API_TOKEN"),
            vk_token=env.str("VK_TOKEN"),
            notification=env.bool("DISABLE_NOTIFICATION"),
            owner_id=env.str("OWNER_ID"),
            amount_post_list=env.int("AMOUNT_POST_LIST"),
            request_period=env.int("REQUEST_PERIOD"),
            sqlite_db_path=env.str("SQLITE_DB_PATH"),
        ))


hidden_vars = load_config('.env')
