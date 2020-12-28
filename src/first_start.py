import sqlite3
import os.path
import sys

print("\n===Config Master===\n")

if os.path.isfile("config.py") is True:
    print("Configuration file already exists! Exiting...")
    sys.exit(1)

# Step 1: database file init 
db_name = input("Enter database file name (default-myTable): ")

if not db_name: 
    db_name = "myTable"

if os.path.isfile(f"{db_name}.db") is True:
    print("A database file with this name already exists! Cancelling...")
    sys.exit(1)
    
conn = sqlite3.connect(f"{db_name}.db")
conn.execute("PRAGMA foreign_keys = 1")
cur = conn.cursor()
cur.execute("CREATE TABLE user_data(user_id INTEGER NOT NULL PRIMARY KEY, user_name TEXT NOT NULL, user_lang TEXT, folders TEXT)")
cur.execute("CREATE TABLE folders(folder_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, folder_name TEXT NOT NULL, user_id INTEGER NOT NULL, audio_sample_count INTEGER, FOREIGN KEY (user_id) REFERENCES user_data(user_id))")
cur.execute("CREATE TABLE audio_samples(audio_sample_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, audio_sample_name TEXT NOT NULL, folder_id INTEGER NOT NULL, user_id INTEGER NOT NULL, file_unique_id TEXT NOT NULL,FOREIGN KEY(folder_id) REFERENCES folders(folder_id), FOREIGN KEY(user_id) REFERENCES user_data(user_id))")
conn.commit()

# Step 2: configuration file init
tlgrm_bot_api = input("Enter Telegram bot API token: ")
audfprint_mode = input("Select the audfprint working mode: \n    0 - Fast audio recognition speed, but worse accuracy\n    1 - High recognition accuracy, but will take longer time\nEnter 0 or 1: ")

with open("config.py", "w") as file:
    file.write(f"API_TOKEN = '{tlgrm_bot_api}'" + '\n')
    file.write(f"DATABASE_NAME = '{db_name}.db'" + '\n')
    file.write(f"audfprint_mode = '{audfprint_mode}'")
    
print("Done!")
