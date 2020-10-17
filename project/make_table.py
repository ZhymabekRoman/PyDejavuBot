import sqlite3
import os.path

if os.path.isfile('myTable.db') is True:
    print("Файл существует! Отмена ...")
    exit()

conn = sqlite3.connect('myTable.db')
cur = conn.cursor()

cur.execute("CREATE TABLE users(user_id TEXT, lang TEXT, projects TEXT)")
conn.commit()
print("Готово !!!")