# -*- coding: utf-8 -*-
# SCRIPT # ======================================================================================================================
# Name...........: PyDejavuBot - Free Open Source Telegram Bot, designed for recognize a melody.
# File name......: backend.py
# Description ...: Is designed to work with the backend functions (file download, audio normalization, audio integrety check and etc)
# Author ........: ZhymabekRoman
# ===============================================================================================================================
import logging
import main

async def download_file(message, file_id, destination):
    message_text = message.html_text + "\n\nЗагрузка файла..."
    await message.edit_text(message_text + " Выполняем...", parse_mode="HTML")
    try:
        await bot.download_file_by_id(file_id, destination)
    except Exception as ex:
        managment_msg = await message.edit_text(message_text + " Критическая ошибка, отмена...", parse_mode="HTML")
        logging.exception(ex)
        raise
    else:
        managment_msg = await message.edit_text(message_text + " Готово ✅", parse_mode="HTML")
    return managment_msg

async def check_audio_integrity_and_convert(message, input_file, output_file):
    message_text = message.html_text + "\n\nПроверка аудио файла на целостность и конвертируем в формат mp3 через ffmpeg..."
    await message.edit_text(message_text + " Выполняем...", parse_mode="HTML")
    try:
        cmd = ['ffmpeg', '-nostdin','-hide_banner', '-loglevel', 'panic', '-i', input_file,'-vn', output_file]
        proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await proc.communicate()
        logging.info(f'[{cmd!r} exited with {proc.returncode}]')
        logging.info(f'[stdout]\n{stdout.decode()}')
        logging.info(f'[stderr]\n{stderr.decode()}')
        if os.path.exists(output_file) is False or proc.returncode == 1:
            raise
    except Exception as ex:
        managment_msg = await message.edit_text(message_text + " Критическая ошибка, отмена...", parse_mode="HTML")
        logging.exception(ex)
        raise
    else:
        managment_msg = await message.edit_text(message_text + " Готово ✅", parse_mode="HTML")
    return managment_msg

async def audio_normalization(message, input_file, output_file):
    message_text = message.html_text + "\n\nНормализация аудио..."
    await message.edit_text(message_text + " Выполняем...", parse_mode="HTML")
    try:
        cmd = ['ffmpeg-normalize', '-q', input_file, '-c:a', 'libmp3lame', '-o', output_file]
        proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await proc.communicate()
        logging.info(f'[{cmd!r} exited with {proc.returncode}]')
        logging.info(f'[stdout]\n{stdout.decode()}')
        logging.info(f'[stderr]\n{stderr.decode()}')
        if os.path.exists(output_file) is False or proc.returncode == 1:
            raise
    except Exception as ex:
        managment_msg = await message.edit_text(message_text + " Критическая ошибка, отмена...", parse_mode="HTML")
        logging.exception(ex)
        raise
    else:
        managment_msg = await message.edit_text(message_text + " Готово ✅", parse_mode="HTML")
    return managment_msg

async def analyze_audio_sample(message, input_file, fingerprint_db):
    message_text = message.html_text + "\n\nРегистрируем аудио хэши в база данных..."
    await message.edit_text(message_text + " Выполняем...", parse_mode="HTML")
    try:
        if os.path.exists(fingerprint_db) is False:
            db_hashes_add_method = 'new'
        elif os.path.exists(fingerprint_db) is True:
            db_hashes_add_method = 'add'
        if config.audfprint_mode == '0':
            cmd = ['python3', 'library/audfprint-master/audfprint.py', db_hashes_add_method, '-d', fingerprint_db, input_file, '-n', '120', '-X', '-F', '18']
        elif config.audfprint_mode == '1':
            cmd = ['python3', 'library/audfprint-master/audfprint.py', db_hashes_add_method, '-d', fingerprint_db, input_file]
        proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await proc.communicate()
        logging.info(f'[{cmd!r} exited with {proc.returncode}]')
        logging.info(f'[stdout]\n{stdout.decode()}')
        logging.info(f'[stderr]\n{stderr.decode()}')
        if os.path.exists(fingerprint_db) is False or proc.returncode == 1:
            raise
    except Exception as ex:
        managment_msg = await message.edit_text(message_text + " Критическая ошибка, отмена...", parse_mode="HTML")
        logging.exception(ex)
        raise
    else:
        managment_msg = await message.edit_text(message_text + " Готово ✅", parse_mode="HTML")
    return managment_msg
    
async def match_audio_query(message, input_file, fingerprint_db):
    message_text = message.html_text + "\n\nИщем аудио хэши в базе данных..."
    await message.edit_text(message_text + " Выполняем...", parse_mode="HTML")
    try:
        if config.audfprint_mode == '0':
            cmd = ['python3', 'library/audfprint-master/audfprint.py', 'match', '-d', fingerprint_db, input_file, '-n', '120', '-D', '2000', '-X', '-F', '18']
        elif config.audfprint_mode == '1':
            cmd = ['python3', 'library/audfprint-master/audfprint.py', 'match', '-d', fingerprint_db, input_file]
        proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await proc.communicate()
        logging.info(f'[{cmd!r} exited with {proc.returncode}]')
        logging.info(f'[stdout]\n{stdout.decode()}')
        logging.info(f'[stderr]\n{stderr.decode()}')
        if os.path.exists(fingerprint_db) is False or proc.returncode == 1:
            raise
    except Exception as ex:
        managment_msg = await message.edit_text(message_text + " Критическая ошибка, отмена...", parse_mode="HTML")
        logging.exception(ex)
        raise
    else:
        managment_msg = await message.edit_text(message_text + f" Готово ✅\n\nРезультат:\n<code>{stdout.decode()}</code>\n", parse_mode="HTML")
    return managment_msg

async def delete_audio_hashes(message, fingerprint_db, sample_name):
    try:
        cmd = ['python3', 'library/audfprint-master/audfprint.py', 'remove', '-d', fingerprint_db, sample_name, '-H', '2']
        proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await proc.communicate()
        logging.info(f'[{cmd!r} exited with {proc.returncode}]')
        logging.info(f'[stdout]\n{stdout.decode()}')
        logging.info(f'[stderr]\n{stderr.decode()}')
    except Exception as ex:
        pass
