import sqlite3
import os
import sys
from other import base64_encode

USER_DATA_PATH="user_data"

print("\n===Config Master===\n")

if os.path.isdir(f"{USER_DATA_PATH}/") is True:
    print("Users data and configuration folder is already exists! Exiting...")
    sys.exit(1)
else:
    os.makedirs(USER_DATA_PATH)

# Step 1: database file init
db_name = input("Enter database file name (default-myTable): ")

if not db_name:
    db_name = "myTable"

conn = sqlite3.connect(f"{USER_DATA_PATH}/{db_name}.db")
conn.execute("PRAGMA foreign_keys = 1")
cur = conn.cursor()
cur.execute("CREATE TABLE user_data(user_id INTEGER NOT NULL PRIMARY KEY, user_name TEXT NOT NULL, user_lang TEXT, folders TEXT)")
cur.execute("CREATE TABLE folders(folder_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, folder_name TEXT NOT NULL, user_id INTEGER NOT NULL, audio_sample_count INTEGER, FOREIGN KEY (user_id) REFERENCES user_data(user_id))")
cur.execute("CREATE TABLE audio_samples(audio_sample_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, audio_sample_name TEXT NOT NULL, folder_id INTEGER NOT NULL, user_id INTEGER NOT NULL, file_unique_id TEXT NOT NULL,FOREIGN KEY(folder_id) REFERENCES folders(folder_id), FOREIGN KEY(user_id) REFERENCES user_data(user_id))")
conn.commit()

# Step 2: configuration file init
tlgrm_bot_api = input("Enter Telegram bot API token: ")
audfprint_mode = input("Select the audfprint working mode: \n    1 - Fast audio recognition speed, but worse accuracy\n    0 - High recognition accuracy, but will take longer time\nEnter 0 or 1: ")

with open(f"{USER_DATA_PATH}/config.py", "w") as file:
    file.write("# Declare Telegram Bot API token\n")
    file.write(f"API_TOKEN = '{base64_encode(tlgrm_bot_api)}'\n")
    file.write("# Declare users data path\n")
    file.write(f"USER_DATA_PATH = '{USER_DATA_PATH}'\n")
    file.write("# Declare users database path\n")
    file.write(f"DATABASE_PATH = '{USER_DATA_PATH}/{db_name}.db'\n")
    file.write("# Declare audio recognizing mode\n")
    file.write(f"audfprint_mode = '{audfprint_mode}'\n")
    
print("Done!")
