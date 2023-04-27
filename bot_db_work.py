import sqlite3


def write_db(*args):
    sqlite_connection = sqlite3.connect('autoposting_vk/base_id', check_same_thread=False)
    cursor = sqlite_connection.cursor()
    cursor.execute(
        f"INSERT INTO APPEAL (TIME, "
        f"ID, "
        f"FIRST_NAME, "
        f"LAST_NAME, "
        f"USERNAME, "
        f"MESSAGE_ID) VALUES (?, ?, ?, ?, ?, ?)", args)
    sqlite_connection.commit()
