import sqlite3

from config import hidden_vars


def check_visitors() -> str:
    sq_connect = sqlite3.connect(hidden_vars.tg_bot.sqlite_db_path, check_same_thread=False)
    sq_cur = sq_connect.cursor()
    sq_cur.execute(
        f"SELECT FIRST_NAME, LAST_NAME, USERNAME, ID, TIME "
        f"FROM APPEAL "
        f"ORDER BY TIME DESC "
        f"LIMIT 10"
    )
    result = '\n'.join(f"{item[4]} {item[0]} {item[1]} {item[2]} {item[3]}\n" for item in sq_cur.fetchall())
    return result
