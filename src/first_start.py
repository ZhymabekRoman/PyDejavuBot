import sqlite3
import os.path

print("Config Master")

if os.path.isfile("config.py") is True:
    print("Файл конфигурации или базы данных существует! Отмена ...")
    exit()

# Step 1 : database init 
db_name = input("Укажите название db (default-myTable): ")

if db_name == "": db_name = "myTable"

if os.path.isfile("config.py") or os.path.isfile(f"{db_name}.db") is True:
    print("Файл конфигурации или базы данных существует! Отмена ...")
    exit()

conn = sqlite3.connect(f"{db_name}.db")
cur = conn.cursor()

cur.execute("CREATE TABLE  IF NOT EXISTS  users(user_id INTEGER, lang TEXT, folders TEXT)")
conn.commit()

# Step 2 :config init
tlgrm_bot_api = input("Укажите API токен бота: ")
audfprint_mode = input("Выберите качество (0) или скорость (1): ")

with open("config.py", "w") as file:
    file.write(f"API_TOKEN = '{tlgrm_bot_api}'" + '\n')
    file.write(f"database_name = '{db_name}.db'" + '\n')
    file.write(f"audfprint_mode = '{audfprint_mode}'")
print("Готово !!!")
