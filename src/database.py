# -*- coding: utf-8 -*-
# SCRIPT # ======================================================================================================================
# Name...........: PyDejavuBot - Free Open Source Telegram Bot, designed for recognize a melody.
# File name......: database.py
# Description ...: Is designed to work with the database. Is the conductor between databases with the bot master code
# Author ........: ZhymabekRoman
# ===============================================================================================================================

import sqlite3
from user_data import config
# import logging

# logging.basicConfig(level=logging.INFO)

class SQLighter:

    def __init__(self, database=config.DATABASE_PATH):
        self.connection = sqlite3.connect(database)
        self.connection.execute("PRAGMA foreign_keys = ON") # Need for working with foreign keys in db
        self.cursor = self.connection.cursor()

    def select_user_data(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT * FROM user_data Where user_id= :0", {'0': user_id}).fetchone()
    
    def select_user_folders_list(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT folder_name FROM folders Where user_id= :0", {'0': user_id}).fetchall()
            return [folder_name[0] for folder_name in result]
            
    def select_user_audio_samples_list(self, user_id, folder_name):
        folder_id = self.get_folder_id_by_folder_name(user_id, folder_name)
        with self.connection:
            result = self.cursor.execute("SELECT audio_sample_name FROM audio_samples Where user_id= :0 AND folder_id= :1", {'0': user_id, '1': folder_id}).fetchall()
            return [audio_sample[0] for audio_sample in result]
            
    def user_folders_count(self, user_id) -> int:
        """Возвращяет общее количество папок пользывателя"""
        with self.connection:
            user_folders = self.select_user_folders_list(user_id)
            return len(user_folders)
    
    def user_audio_samples_count(self, user_id) -> int:
        """Возвращяет общее количество аудио сэмлов пользывателя"""
        with self.connection:
            user_audio_samples = self.cursor.execute("SELECT audio_sample_name FROM audio_samples Where user_id= :0", {'0': user_id}).fetchall()
            return len(user_audio_samples)
    
    def create_folder(self, user_id, folder_name) -> None:
        """Создает папку"""
        with self.connection:
            self.cursor.execute("INSERT INTO folders (folder_name, user_id, audio_sample_count) VALUES (:0, :1, NULL)", {'0': folder_name, '1': user_id})
            
    def delete_folder(self, user_id, folder_name) -> None:
        """Удаляет папку"""
        folder_id = self.get_folder_id_by_folder_name(user_id, folder_name)
        with self.connection:
            self.cursor.execute("DELETE FROM folders WHERE folder_id= :0 AND user_id= :1", {'0': folder_id, '1': user_id})
     
    def get_folder_id_by_folder_name(self, user_id, folder_name) -> str:
        """Получаем ID папки по названию папки"""
        with self.connection:
            folder_id = self.cursor.execute("SELECT folder_id FROM folders Where folder_name= :1 AND user_id= :0", {'0': user_id, '1': folder_name}).fetchone()[0]
            return folder_id
            
    def create_empety_user_data(self, user_id, user_name) -> None:
        """Регистрирует ID юзера без указания языка"""
        with self.connection:
            self.cursor.execute("INSERT INTO user_data VALUES (:0, :1, :2, :3)", {'0': user_id, '1': user_name, '2': '', '3': '{}'})
            
    def get_user_lang(self, user_id):
        """Возвращяет язык интерфейса пользывателя"""
        with self.connection:
            return self.cursor.execute("SELECT user_lang FROM user_data Where user_id= :0", {'0': user_id}).fetchone()[0]
            
    def set_user_lang(self, user_id, lang_name) -> None:
        """Регистрирует язык интерфейса пользывателя"""
        with self.connection:
            self.cursor.execute("UPDATE user_data SET user_lang = :0 WHERE user_id = :1", {'0': lang_name, '1': user_id})

    def register_audio_sample(self, user_id, folder_name, audio_sample_name, file_id) -> None:
        """Регистрирует сэмпл в папку"""
        folder_id = self.get_folder_id_by_folder_name(user_id, folder_name)
        with self.connection:
            self.cursor.execute("INSERT INTO audio_samples (audio_sample_name, folder_id, user_id, file_unique_id) VALUES (:0, :1, :2, :3)", {'0': audio_sample_name, '1': folder_id, '2': user_id, '3': file_id})
              
    def unregister_audio_sample(self, user_id, folder_name, sample_name) -> None:
        """Удаляет определенный сэмпл из папки"""
        with self.connection:
            folder_id = self.get_folder_id_by_folder_name(user_id, folder_name)
            self.cursor.execute("DELETE FROM audio_samples WHERE audio_sample_name= :0 AND folder_id= :1 AND user_id= :2", {'0': sample_name, '1': folder_id, '2': user_id})
            
    def unregister_all_audio_sample(self, user_id, folder_name) -> None:
        """Удаляет ВСЕ сэмплы из папки"""
        with self.connection:
            folder_id = self.get_folder_id_by_folder_name(user_id, folder_name)
            self.cursor.execute("DELETE FROM audio_samples WHERE folder_id= :0 AND user_id= :1", {'0': folder_id, '1': user_id})
            
    def check_audio_sample_with_same_file_id_in_folder(self, user_id, folder_name, file_unique_id):
        folder_id = self.get_folder_id_by_folder_name(user_id, folder_name)
        with self.connection:
            return self.cursor.execute("SELECT audio_sample_name FROM audio_samples Where file_unique_id= :0 AND folder_id= :1", {'0': file_unique_id, '1': folder_id}).fetchone()
            
    def close(self):
        """ Закрываем текущее соединение с БД """
        self.connection.close()
