# -*- coding: utf-8 -*-
# SCRIPT # ======================================================================================================================
# Name...........: PyDejavuBot - Free Open Source Telegram Bot, designed for recognize a melody.
# File name......: other.py
# Description ...: It stores codes that are not particularly relevant to bot health, but are vital
# Author ........: ZhymabekRoman
# ===============================================================================================================================

# https://stackoverflow.com/a/26853961
def merge_two_dicts(x, y):
    """Given two dictionaries, merge them into a new dict as a shallow copy."""
    z = x.copy()
    z.update(y)
    return z

# https://pynative.com/python-generate-random-string/
def generate_random_string(length):
    """Returns random generated string with a certain quantity letters"""
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

# Не помню откуда взял этот код =)
def check_string_for_except_chars(string):
	"""Поверяет строку на недопустимые символы, в случае если будут то возвращяет словарь с присутсвующими запрещенными символами"""
    exception_chars = '\\\/\|<>\?:"\*'
    find_exceptions = re.compile('([{}])'.format(exception_chars))
    return find_exceptions.findall(string)