# -*- coding: utf-8 -*-
# SCRIPT # ======================================================================================================================
# Name...........: PyDejavuBot - Free Open Source Telegram Bot, designed for recognize a melody.
# File name......: other.py
# Description ...: It stores codes that are not particularly relevant to bot health, but are vital
# Author ........: ZhymabekRoman
# ===============================================================================================================================
import re
import string
import random
import base64
from dataclasses import dataclass
from user_data import config

# https://pynative.com/python-generate-random-string/
def generate_random_string(length: int) -> str:
    """Returns random generated string with a certain quantity letters"""
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

@dataclass
class path:
    """Возвращяет путь к личным папкам пользывателей, а-ля конструктор путей"""
    user_id: str
    user_folder: str

    def tmp_audio_samples(file_name = "") -> str:
        return f'{config.USER_DATA_PATH}/audio_sample/tmp/{self.user_id}/{self.user_folder}/{file_name}'
    def non_normalized_audio_samples(file_name = "") -> str:
        return f'{config.USER_DATA_PATH}/audio_sample/non_normalized/{self.user_id}/{self.user_folder}/{file_name}'
    def normalized_audio_samples(file_name = "") -> str:
        return f'{config.USER_DATA_PATH}/audio_sample/normalized/{self.user_id}/{self.user_folder}/{file_name}'
        
    def tmp_query_audio(file_name = "") -> str:
        return f'{config.USER_DATA_PATH}/query/tmp/{self.user_id}/{self.user_folder}/{file_name}'
    def non_normalized_query_audio(file_name = "") -> str:
        return f'{config.USER_DATA_PATH}/query/non_normalized/{self.user_id}/{self.user_folder}/{file_name}'
    def normalized_query_audio(file_name = "") -> str:
        return f'{config.USER_DATA_PATH}/query/normalized/{self.user_id}/{self.user_folder}/{file_name}'
    
    def fingerprint_db() -> str:
        return f'{config.USER_DATA_PATH}/audio_samples/fingerprint_db/{self.user_id}/{self.user_folder}.fpdb'
    def fingerprint_db_dir_path() -> str:
        return f'{config.USER_DATA_PATH}/audio_samples/fingerprint_db/{self.user_id}/'

# Не помню откуда взял этот код =)
def check_string_for_except_chars(string: str) -> str:
    """Поверяет строку на недопустимые символы, в случае если будут то возвращяет словарь с присутсвующими запрещенными символами"""
    exception_chars = '\\\/\|<>\?:"\*'
    find_exceptions = re.compile('([{}])'.format(exception_chars))
    return find_exceptions.findall(string)
    
def base64_encode(message: str) -> str:
    """Зашифровывает строку в base64"""
    message_bytes = message.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode('ascii')
    return base64_message
    
def base64_decode(base64_message: str) -> str:
    """Расшифровывает base64 строку"""
    base64_bytes = base64_message.encode('ascii')
    message_bytes = base64.b64decode(base64_bytes)
    message = message_bytes.decode('ascii')
    return message