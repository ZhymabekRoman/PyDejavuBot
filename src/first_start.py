import sqlite3
import os.path
print("Config Master")

# Step 1 : database init 
db_name = input("Укажите название db (default-myTable): ")

if db_name == "":
	db_name = "myTable"

if os.path.isfile(f"{db_name}.db") is True:
    print("Файл базы данных существует! Отмена ...")
    exit()

conn = sqlite3.connect(f"{db_name}.db")
cur = conn.cursor()

cur.execute("CREATE TABLE  IF NOT EXISTS  users(user_id TEXT, lang TEXT, projects TEXT)")
conn.commit()

# Step 2 :config init
if os.path.isfile("config.py") is True:
    print("Файл конфигурации существует! Отмена ...")
    exit()

tlgrm_bot_api = input("Укажите API токен бота: ")
audfprint_mode = input("Выберите скорость (0) или качество (1): ")

file = open("config.py", "w")
file.write(f"API_TOKEN = '{tlgrm_bot_api}'" + '\n')
file.write(f"database_name = '{db_name}.db'" + '\n')
file.write(f"audfprint_mode = '{audfprint_mode}'")
file.close()
print("Готово !!!")