import sqlite3
import os.path

db_name = input("Укажите название db: ")

if os.path.isfile(f"{db_name}.db") is True:
    print("Файл существует! Отмена ...")
    exit()

conn = sqlite3.connect(f"{db_name}.db")
cur = conn.cursor()

cur.execute("CREATE TABLE  IF NOT EXISTS  users(user_id TEXT, lang TEXT, projects TEXT)")
conn.commit()
print("Готово !!!")