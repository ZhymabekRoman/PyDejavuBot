# -*- coding: utf-8 -*-
import sqlite3
import json

def merge_two_dicts(x, y):
    """Given two dictionaries, merge them into a new dict as a shallow copy."""
    z = x.copy()
    z.update(y)
    return z

class SQLighter:

    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def select_user_data(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT * FROM users Where user_id= :0", {'0': user_id}).fetchone()
    
    def select_user_folders_list(self, user_id):
        with self.connection:
            return json.loads((self.cursor.execute("SELECT projects FROM users Where user_id= :0", {'0': user_id}).fetchone())[0])
    
    def select_user_folders_count(self, user_id):
        with self.connection:
            out =  json.loads((self.cursor.execute("SELECT projects FROM users Where user_id= :0", {'0': user_id}).fetchone())[0])
            return len(out)
    
    def create_folder(self, user_id, folder_name):
        with self.connection:
            ### Получаем папки пользывателя
            folders_list = self.select_user_folders_list(user_id)
            ### Создаем словарь с названием папки и стренным внутри еще одним пустым словарем, что бы хранить там данные сэмлов : )
            new_folder = {folder_name: {}}
            ### Мерджуем два словаря : новый и старый
            data_to_add = merge_two_dicts(folders_list, new_folder)
            ### Коммитим, предварительно упаковав в json : )
            self.cursor.execute("UPDATE users SET projects =  :0 WHERE User_id = :1", {'0': json.dumps(data_to_add), '1': user_id})

    def delete_folder(self, user_id, folder_name):
        with self.connection:
            ### Получаем папки пользывателя
            folders_list = self.select_user_folders_list(user_id)
            ### Удаляем папку от туда
            del folders_list[folder_name]
            ### Коммитим !
            self.cursor.execute("UPDATE users SET projects =  :0 WHERE user_id = :1", {'0': json.dumps(folders_list), '1': user_id})

    def create_empety_user_data(self, user_id):
        with self.connection:
            self.cursor.execute("INSERT INTO users VALUES (:0, :1, :2)", {'0': user_id, '1': '', '2': '{}'})
            
    def set_lang(self, user_id, lang_name):
        with self.connection:
            self.cursor.execute("UPDATE users SET lang = :0 WHERE user_id = :1", {'0': lang_name, '1': user_id})
            
    def register_audio_sample(self, user_id, folder_name, sample_name, file_id):
        with self.connection:
            ### Получаем список сэмплов текущей папкм
            folder_samples = self.select_user_folders_list(user_id)[folder_name]
            ### Создаем словарь с названием нового сэмла и file_id сэмпла : )
            new_sample = {sample_name: file_id}
            ### Мерджуем старые сэмплы с новыми из текущей папкм
            curent_folder_samples = merge_two_dicts(folder_samples, new_sample)
            ### Обновляем  сэмплы текущей папки в список папок
            ## Но прежде получаем весь список папкок текущего пользывателя
            folders_list = self.select_user_folders_list(user_id)
            folders_list[folder_name] = curent_folder_samples
            ### Коммитим !
            self.cursor.execute("UPDATE users SET projects =  :0  WHERE User_id = :1", {'0': json.dumps(folders_list), '1': user_id})
            
    def unregister_audio_sample(self, user_id, folder_name, sample_name):
        with self.connection:
            ### Получаем список сэмплов текущей папкм
            folder_samples = self.select_user_folders_list(user_id)[folder_name]
            ### Удаляем сэмпл текущей папки
            del folder_samples[sample_name]
            ### Обновляем  сэмплы текущей папки в список папок
            ## Но прежде получаем весь список папкок текущего пользывателя
            folders_list = self.select_user_folders_list(user_id)
            folders_list[folder_name] =folder_samples
            ### Коммитим !
            self.cursor.execute("UPDATE users SET projects =  :0  WHERE User_id = :1", {'0': json.dumps(folders_list), '1': user_id})
            
    def unregister_all_audio_sample(self, user_id, folder_name):
        with self.connection:
            ### Удаляем ВСЕ сэмпл текущей папки
            ### Обновляем  сэмплы текущей папки в список папок
            ## Но прежде получаем весь список папкок текущего пользывателя
            folders_list = self.select_user_folders_list(user_id)
            folders_list[folder_name] = {}
            ### Коммитим !
            self.cursor.execute("UPDATE users SET projects =  :0  WHERE User_id = :1", {'0': json.dumps(folders_list), '1': user_id})
            
    def close(self):
        """ Закрываем текущее соединение с БД """
        self.connection.close()