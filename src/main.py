# -*- coding: utf-8 -*-
# SCRIPT # ======================================================================================================================
# Name...........: PyDejavuBot - Free Open Source Telegram Bot, designed for recognize a melody.
# File name......: main.py
# Description ...: Main PyDejavuBot's code
# Author ........: ZhymabekRoman
# ===============================================================================================================================

import os
import sys
import shutil    
import logging
import asyncio

# Import configuration file
try:
    from user_data import config
except ImportError:
    print("Please first configure config file via script 'first_start.py'")
    sys.exit(1)

from database import SQLighter
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import BotBlocked, MessageNotModified
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from other import *

# Initalialization API token for work with Telegram Bot
API_TOKEN = base64_decode(config.API_TOKEN)

# Configure Memory Storage
memory_storage = MemoryStorage()  ### TODO - Redis storage

# Configure logging
logging.basicConfig(level=logging.INFO)
# logging.basicConfig(level=logging.DEBUG) 

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=memory_storage)

# Initialize connection with db
db = SQLighter(config.DATABASE_PATH)

# Initialize callback data factory
language_cb = CallbackData("language_settings", "language_code")
manage_folder_cb = CallbackData("manage_folder_menu", "folder_name")
remove_folder_cb = CallbackData("remove_folder_message", "folder_name")
remove_folder_process_cb = CallbackData("remove_folder_process", "folder_name")
upload_audio_sample_cb = CallbackData("upload_audio_sample_message", "folder_name")
remove_audio_sample_cb = CallbackData("remove_audio_sample_message", "folder_name")
recognize_query_cb = CallbackData("recognize_query_message", "folder_name")

AVAILABLE_LANGUAGES = {
        "En": {'flag': "🇺🇸", 'name': "English"},
        "Ru": {'flag': "🇷🇺", 'name': "Русский"},
        "Uk": {'flag': "🇺🇦", 'name': "Українська"}
    }

class CreateFolder(StatesGroup):
    step_1 = State()
    step_2 = State()
class Upload_Sample(StatesGroup):
    step_1 = State()
    step_2 = State()
class RemoveSample(StatesGroup):
    step_1 = State()
class UploadQuery(StatesGroup):
    step_1 = State()

curent_folder_name = {}

### CRITICAL TODO №1 - DON'T USE GLOBAL VARIABLES
def get_selected_folder_name(user_id):
    global curent_folder_name
    return str(curent_folder_name[user_id])

def set_selected_folder_name(user_id, set_name):
    global curent_folder_name
    curent_folder_name[user_id] = str(set_name)

def unset_selected_folder_name(user_id):
    global curent_folder_name
    curent_folder_name[user_id] = str("")

async def download_file(message, file_id, destination) -> types.Message:
    message_text = message.html_text + "\n\nЗагрузка файла..."
    await message.edit_text(message_text + " Выполняем...", parse_mode="HTML")
    try:
        await bot.download_file_by_id(file_id, destination)
    except Exception as ex:
        managment_msg = await message.edit_text(message_text + " Критическая ошибка, отмена...", parse_mode="HTML")
        raise
    else:
        managment_msg = await message.edit_text(message_text + " Готово ✅", parse_mode="HTML")
    return managment_msg

async def audio_processing(message, input_file, output_file):
    message_text = message.html_text + "\n\nПроверка на целостность, нормализация и конвертация аудио файла в формат mp3 через ffmpeg..."
    await message.edit_text(message_text + " Выполняем...", parse_mode="HTML")
    try:
        cmd = ['ffmpeg-normalize', '-q', '-vn', input_file, '-c:a', 'libmp3lame', '-o', output_file]
        proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await proc.communicate()
        logging.info(f'[{cmd!r} exited with {proc.returncode}]')
        logging.info(f'[stdout]\n{stdout.decode()}')
        logging.info(f'[stderr]\n{stderr.decode()}')
        if os.path.exists(output_file) is False or proc.returncode == 1:
            raise
    except Exception as ex:
        managment_msg = await message.edit_text(message_text + " Критическая ошибка, отмена...", parse_mode="HTML")
        raise
    else:
        managment_msg = await message.edit_text(message_text + " Готово ✅", parse_mode="HTML")
    return managment_msg

async def register_audio_hashes(message, input_file, fingerprint_db):
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
        raise
    else:
        managment_msg = await message.edit_text(message_text + f" Готово ✅\n\nРезультат:\n<code>{stdout.decode()}</code>\n", parse_mode="HTML")
    return managment_msg

async def delete_audio_hashes(message, fingerprint_db, sample_name):
    message_text = message.html_text + "\n\nУдаляем аудио хэши..."
    await message.edit_text(message_text + " Выполняем...", parse_mode="HTML")
    try:
        cmd = ['python3', 'library/audfprint-master/audfprint.py', 'remove', '-d', fingerprint_db, sample_name, '-H', '2']
        proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await proc.communicate()
        logging.info(f'[{cmd!r} exited with {proc.returncode}]')
        logging.info(f'[stdout]\n{stdout.decode()}')
        logging.info(f'[stderr]\n{stderr.decode()}')
        if os.path.exists(fingerprint_db) is False or proc.returncode == 1:
            raise
    except Exception as ex:
       managment_msg = await message.edit_text(message_text + " Критическая ошибка, отмена...", parse_mode="HTML")
       raise
    else:
        managment_msg = await message.edit_text(message_text + " Готово ✅", parse_mode="HTML")
    return managment_msg

@dp.message_handler(commands=['start'], state='*')
async def start_cmd_message(message: types.Message):
    # Проверяем на существование текущего пользывателя в БД
    # Если не существует тогда регистрируем ID пользывателя в БД без указания языка интерфейса
    logging.info(message)
    if db.select_user_data(message.chat.id) is None:
        db.create_empety_user_data(message.chat.id, message.from_user.username)
    # Проверка языка интерфейса в БД
    # Если не существует тогда посылвает юзеру сообщение о выборе языка
    if not db.get_user_lang(message.chat.id):
        await language_settings_message(message, 'start')
    else:
        await main_menu_message(message, 'reply')

@dp.callback_query_handler(lambda c: c.data == 'bot_settings_message')
async def bot_settings_message(callback_query: types.CallbackQuery):
    keyboard_markup = types.InlineKeyboardMarkup()
    back_btn = types.InlineKeyboardButton('«      ', callback_data= 'welcome_message')
    lang_btn = types.InlineKeyboardButton(f'Язык интерфейса : {db.get_user_lang(callback_query.message.chat.id)}', callback_data= 'edit_lang')
    keyboard_markup.row(lang_btn)
    keyboard_markup.row(back_btn)
    await callback_query.message.edit_text("Настройки бота:", reply_markup=keyboard_markup)
    await bot.answer_callback_query(callback_query.id)

@dp.callback_query_handler(lambda c: c.data == 'about_bot_message')
async def about_bot_message(callback_query: types.CallbackQuery):
    keyboard_markup = types.InlineKeyboardMarkup()
    back_btn = types.InlineKeyboardButton('«      ', callback_data= 'welcome_message')
    keyboard_markup.row(back_btn)
    await callback_query.message.edit_text(
        "LenDejavuBot - бот предназначенный для решения музыкальных викторин. Бот специально разработан для Павлодарского музыкального колледжа\n\n"
        "Разработчик ботка : @Zhymabek_Roman\n"
        "Тех.поддержка : @Zhymabek_Roman", 
        reply_markup=keyboard_markup)
    await bot.answer_callback_query(callback_query.id)

async def quiz_mode_step_0(message: types.Message):
    keyboard_markup = types.InlineKeyboardMarkup()
    for folder_name in db.select_user_folders_list(message.chat.id):
        get_sample_count = len(db.select_user_audio_samples_list(message.chat.id, folder_name))
        folder_btn = types.InlineKeyboardButton(f"{folder_name} ({get_sample_count})", callback_data = "set_" + folder_name)
        keyboard_markup.row(folder_btn)
    back_btn = types.InlineKeyboardButton('«      ', callback_data= 'welcome_message')
    keyboard_markup.row(back_btn)
    await message.edit_text("Выберите папку : ", reply_markup=keyboard_markup)   
    await CreateFolder.step_2.set()
    
async def main_menu_message(message: types.Message, messaging_type):
    keyboard_markup = types.InlineKeyboardMarkup()
    folder_list_btns = types.InlineKeyboardButton('Папки 📂', callback_data= 'folders_list')
    about_btns = types.InlineKeyboardButton('О боте 🤖', callback_data= 'about_bot_message')
    setings_btns = types.InlineKeyboardButton('Настройки  🎛️', callback_data= 'bot_settings_message')
    quiz_mode_btn = types.InlineKeyboardButton('Распознать 🔎🎵', callback_data= 'quiz_mode_0')
    keyboard_markup.row(folder_list_btns)
    keyboard_markup.row(about_btns, setings_btns)
    keyboard_markup.row(quiz_mode_btn)
    if messaging_type == 'edit':
        await message.edit_text("Главное меню : ", reply_markup=keyboard_markup)
    elif messaging_type == 'reply':
        await message.reply("Главное меню : ", reply_markup=keyboard_markup)

async def language_settings_message(message: types.Message, messaging_type= 'start'):
    keyboard = types.InlineKeyboardMarkup()
    for lang_code, lang_info in AVAILABLE_LANGUAGES.items():
        language_label = f"{lang_info['flag']} {lang_info['name']}"
        button = types.InlineKeyboardButton(text=language_label, callback_data=language_cb.new(lang_code))
        keyboard.add(button)
    message_text = "Please select your language:"
    if messaging_type == 'start':
        await message.reply(message_text, reply_markup=keyboard)
    elif messaging_type == 'edit':
        await message.edit_text(message_text, reply_markup=keyboard)

@dp.callback_query_handler(language_cb.filter())
async def set_language_message(call: types.CallbackQuery, callback_data: dict):
    db.set_user_lang(call.message.chat.id, callback_data['language_code'])
    await call.answer(f"🎚Настройки : Выбран {callback_data['language_code']} язык!")
    await main_menu_message(call.message, 'edit')

async def folder_list_menu_message(message: types.Message, messaging_type):
    unset_selected_folder_name(message.chat.id)
    
    keyboard_markup = types.InlineKeyboardMarkup()
    create_new_folder_btn = types.InlineKeyboardButton('Создать новую папку 🗂', callback_data='create_new_folder')
    keyboard_markup.row(create_new_folder_btn)
    
    for folder_name in db.select_user_folders_list(message.chat.id):
        get_sample_count = len(db.select_user_audio_samples_list(message.chat.id, folder_name))
        folder_btn = types.InlineKeyboardButton(f"{folder_name} ({get_sample_count})", callback_data=manage_folder_cb.new(folder_name))
        keyboard_markup.row(folder_btn)
 
    back_btn = types.InlineKeyboardButton('«      ', callback_data= 'welcome_message')
    keyboard_markup.row(back_btn)
    
    if messaging_type == 'start':
        await message.answer(f"Менеджер папок :\n\nОбщее количество папок: {db.user_folders_count(message.chat.id)}", reply_markup=keyboard_markup)
    elif messaging_type == 'edit':
        await message.edit_text(f"Менеджер папок :\n\nОбщее количество папок: {db.user_folders_count(message.chat.id)}", reply_markup=keyboard_markup)
    
async def create_folder_step_1_message(message: types.Message):
    keyboard_markup = types.InlineKeyboardMarkup()
    back_btn = types.InlineKeyboardButton('«      ', callback_data = 'folders_list')
    keyboard_markup.row(back_btn)
    await message.edit_text("Введите название вашей папки : ", reply_markup=keyboard_markup)   
    await CreateFolder.step_1.set()

@dp.message_handler(state=CreateFolder.step_1, content_types=types.ContentTypes.TEXT)
async def create_folder_step_2_message(message: types.Message, state: FSMContext):
    async with state.proxy() as user_data:
        user_data['folder_name'] = message.text.replace('\n',' ')
    
    # Проверяем количество символов в названии папки
    if len(user_data['folder_name']) >= 20:
        keyboard_markup = types.InlineKeyboardMarkup()
        back_btn = types.InlineKeyboardButton('«      ', callback_data = 'folders_list')
        keyboard_markup.row(back_btn)
        await message.reply('Название папки превышает 20 символов', reply_markup=keyboard_markup)
        return
    # Ищем название данной папки в БД 
    if [x.lower() for x in db.select_user_folders_list(message.chat.id)] == user_data['folder_name'].lower():
        keyboard_markup = types.InlineKeyboardMarkup()
        back_btn = types.InlineKeyboardButton('«      ', callback_data = 'folders_list')
        keyboard_markup.row(back_btn)
        await message.reply('Данная папка уже существует! Введите другое имя', reply_markup=keyboard_markup)
        return
    
    # Проверяем название папки на недопустимые символы
    if check_string_for_except_chars(user_data['folder_name']):
        keyboard_markup = types.InlineKeyboardMarkup()
        back_btn = types.InlineKeyboardButton('«      ', callback_data = 'folders_list')
        keyboard_markup.row(back_btn)
        await message.reply(f'Название папки "{user_data["folder_name"]}" содержит недопустимые символы: {check_string_for_except_chars(user_data["folder_name"])}', reply_markup=keyboard_markup)
        return 
    
    await state.finish()
    
    path_list = path(message.chat.id, user_data['folder_name'])
    os.makedirs(path_list.tmp_audio_samples())
    os.makedirs(path_list.processed_audio_samples())
    os.makedirs(path_list.tmp_query_audio())
    os.makedirs(path_list.processed_query_audio())
    try:
        os.makedirs(path_list.fingerprint_db_dir_path())
    except:
        pass
    
    db.create_folder(message.chat.id, user_data['folder_name'])
    
    await message.reply(f'Папка "{user_data["folder_name"]}" создана!')
    await folder_list_menu_message(message, 'start') 

@dp.callback_query_handler(manage_folder_cb.filter(), state='*')
async def manage_folder_menu_message(call: types.CallbackQuery, callback_data: dict):
    print(callback_data)
    folder_name = callback_data['folder_name']
    set_selected_folder_name(call.message.chat.id, folder_name)
    
    keyboard_markup = types.InlineKeyboardMarkup()
    upload_audio_samples_btn = types.InlineKeyboardButton('Загрузить аудио сэмплы', callback_data=upload_audio_sample_cb.new(folder_name))
    keyboard_markup.row(upload_audio_samples_btn)
    remove_audio_samples_btn = types.InlineKeyboardButton('Удалить аудио сэмплы', callback_data=remove_audio_sample_cb.new(folder_name))
    keyboard_markup.row(remove_audio_samples_btn)
    quiz_mode_btn = types.InlineKeyboardButton('Режим Викторины', callback_data=recognize_query_cb.new(folder_name))
    keyboard_markup.row(quiz_mode_btn)
    delete_btn = types.InlineKeyboardButton('Удалить папкy', callback_data=remove_folder_cb.new(folder_name))
    keyboard_markup.row(delete_btn)
    back_btn = types.InlineKeyboardButton('«      ', callback_data= 'folders_list')
    keyboard_markup.row(back_btn)
    
    samples_name = ""
    for i, b in enumerate(db.select_user_audio_samples_list(call.message.chat.id, folder_name), 1):
        samples_name += str(f"{i}) {b}\n")
        
    samples_count = len(db.select_user_audio_samples_list(call.message.chat.id, folder_name))
               
    await call.message.edit_text(
                               f"Вы работаете с папкой : {folder_name}\n\n"
                               f"Количество аудио сэмплов: {samples_count}\n"
                               f"Список аудио сэмлов :\n{samples_name}\n"
                               "Ваши действия - ", reply_markup=keyboard_markup)

@dp.callback_query_handler(remove_folder_cb.filter())
async def delete_folder_step_1_message(call: types.CallbackQuery, callback_data: dict):
    folder_name = callback_data['folder_name']
    
    keyboard_markup = types.InlineKeyboardMarkup()
    delete_btn = types.InlineKeyboardButton('Да!', callback_data=remove_folder_process_cb.new(folder_name))
    back_btn = types.InlineKeyboardButton('«      ', callback_data=manage_folder_cb.new(folder_name))
    keyboard_markup.row(delete_btn)
    keyboard_markup.row(back_btn)
    await call.message.edit_text(
                    f'Вы действительно хотите удалить папку "{folder_name}"?\n'
                    f'Также будут удалены ВСЕ аудио сэмплы, которые находятся в папке "{folder_name}".\n\n'
                    "<b>ВНИМАНИЕ! ЭТО ДЕЙСТВИЕ НЕЛЬЗЯ ОТМЕНИТЬ !!!</b>",
                    parse_mode="HTML",
                    reply_markup=keyboard_markup)

@dp.callback_query_handler(remove_folder_process_cb.filter())
async def delete_folder_step_2_message(call: types.CallbackQuery, callback_data: dict):
    folder_name = callback_data['folder_name']
    path_list = path(call.message.chat.id)
    ### Todo !
    try:
        # Delete all folders
        shutil.rmtree(path_list.tmp_audio_samples())
        shutil.rmtree(path_list.processed_audio_samples())
        shutil.rmtree(path_list.tmp_query_audio())
        shutil.rmtree(path_list.processed_query_audio())
        # Delete audiofingerprint database
        os.remove(path_list.fingerprint_db())
    except:
        pass
    finally:
        db.unregister_all_audio_sample(call.message.chat.id, folder_name)
        db.delete_folder(call.message.chat.id, folder_name)
    await call.message.edit_text(f'Папка "{folder_name}" удалена!')
    await folder_list_menu_message(call.message, 'start')

@dp.callback_query_handler(upload_audio_sample_cb.filter())
async def upload_audio_sample_message(call: types.CallbackQuery, callback_data: dict):
    folder_name = callback_data['folder_name']
    
    keyboard_markup = types.InlineKeyboardMarkup()
    back_btn = types.InlineKeyboardButton('«      ', callback_data = manage_folder_cb.new(get_selected_folder_name(call.message.chat.id)))
    keyboard_markup.row(back_btn)
    await call.message.edit_text(
                    f'Вы работаете с папкой "{folder_name}", в режиме загрузки аудио сэмплов\n\n'
                    'Поддерживаемые форматы - mp3, wav, wma, ogg, flac, aac;\n'
                    'Максимальный размер файла - 20мб. Это максимальный размер для Telegram ботов;\n'
                    'Файлы нужно загружать по одному !\n\n'
                    'Жду от тебя аудио сэмпл',
                    parse_mode="HTML", 
                    reply_markup=keyboard_markup)
    await Upload_Sample.step_1.set()

@dp.message_handler(state=Upload_Sample.step_1, content_types=types.ContentTypes.DOCUMENT | types.ContentTypes.AUDIO | types.ContentTypes.VIDEO)
async def upload_audio_sample_step_1_message(message: types.Message, state: FSMContext):
    async with state.proxy() as user_data:
        user_data['audio_sample_message'] = message
        user_data['audio_sample_content_type'] = message.content_type
        
        if user_data["audio_sample_content_type"] == "document":
            user_data['audio_sample_file_info'] = user_data["audio_sample_message"].document
            name_file = user_data["audio_sample_message"].document.file_name
        elif user_data["audio_sample_content_type"] == "audio":
            user_data['audio_sample_file_info'] = user_data["audio_sample_message"].audio
            name_file = user_data["audio_sample_message"].audio.file_name ### New in Bot API 5.0
   
        user_data['audio_sample_file_name'] = os.path.splitext(name_file)[0]
        user_data['audio_sample_file_extensions'] = os.path.splitext(name_file)[1]
        
    # TODO: bypass file size limit
#    if int(user_data["audio_sample_file_info"].file_size) >= 20871520:
#        keyboard_markup = types.InlineKeyboardMarkup()
#        back_btn = types.InlineKeyboardButton('«      ', callback_data= get_selected_folder_name(message.chat.id))
#        keyboard_markup.row(back_btn)
#        await message.reply('Размер файла превышает 20 mb. Отправьте другой файл', reply_markup=keyboard_markup)
#        return
    
    ### Проверка на загруженность файла в текущей папки через db
    file_unique_id = user_data["audio_sample_file_info"].file_unique_id
    db_audio_sample_unique_name = db.check_audio_sample_with_same_file_id_in_folder(message.chat.id, get_selected_folder_name(message.chat.id), file_unique_id)
    if db_audio_sample_unique_name:
        keyboard_markup = types.InlineKeyboardMarkup()
        back_btn = types.InlineKeyboardButton('«      ', callback_data= get_selected_folder_name(message.chat.id))
        keyboard_markup.row(back_btn)
        await message.reply(f'В папке "{get_selected_folder_name(message.chat.id)}" этот аудио сэмпл уже существует под названием "{db_audio_sample_unique_name[0]}"\nОтправьте другой файл', reply_markup=keyboard_markup)
        return
     
    # Проверяем расширение файла
    if user_data["audio_sample_file_extensions"].lower() in ('.aac','.wav', '.mp3', '.wma', '.ogg', '.flac'):
        await Upload_Sample.step_2.set()
        
        keyboard_markup = types.InlineKeyboardMarkup()
        back_btn = types.InlineKeyboardButton('«      ', callback_data= get_selected_folder_name(message.chat.id))
        keyboard_markup.row(back_btn)
        await message.reply(
                        f'Название вашего аудио файла : <code>{user_data["audio_sample_file_name"]}</code>\n\n'
                        'Введите название аудио сэмпла. Это название будет отображатся во время распознавания викторины',
                        parse_mode="HTML",
                        reply_markup=keyboard_markup)
    elif not user_data["audio_sample_file_extensions"]:
        keyboard_markup = types.InlineKeyboardMarkup()
        back_btn = types.InlineKeyboardButton('«      ', callback_data= get_selected_folder_name(message.chat.id))
        keyboard_markup.row(back_btn)
        await message.reply('Мы не можем определить формат аудио записи. Возможно название файла очень длинное.\nИзмените название файла на более короткую и повторите попытку еще раз', reply_markup=keyboard_markup)
        return
    else:
        keyboard_markup = types.InlineKeyboardMarkup()
        back_btn = types.InlineKeyboardButton('«      ', callback_data= get_selected_folder_name(message.chat.id))
        keyboard_markup.row(back_btn)
        await message.reply(f'Мы "{user_data["audio_sample_file_extensions"]}" формат не принемаем, пришлите в другом формате\n\n', reply_markup=keyboard_markup)
        return

@dp.message_handler(state= Upload_Sample.step_2, content_types=types.ContentTypes.TEXT)
async def upload_audio_sample_step_2_message(message: types.Message, state: FSMContext):
    async with state.proxy() as user_data:
        user_data['audio_sample_name'] = message.text.replace('\n',' ')
        
    file_id = user_data["audio_sample_file_info"].file_id
    audio_sample_name = f'{user_data["audio_sample_name"]}'
    audio_sample_full_name = f'{user_data["audio_sample_name"]}{user_data["audio_sample_file_extensions"]}'
    path_list = path(message.chat.id, get_selected_folder_name(message.chat.id))
    
    # Проверяем количество символов в названии сэмпла
    if len(user_data["audio_sample_name"]) >= 90:
        keyboard_markup = types.InlineKeyboardMarkup()
        back_btn = types.InlineKeyboardButton('«      ', callback_data = get_selected_folder_name(message.chat.id))
        keyboard_markup.row(back_btn)
        await message.reply('Название сэмпла превышает 90 символов, введите другое имя', reply_markup=keyboard_markup)
        return
    
    # Проверяем строку на недопустимые символы
    if check_string_for_except_chars(user_data["audio_sample_name"]):
        keyboard_markup = types.InlineKeyboardMarkup()
        back_btn = types.InlineKeyboardButton('«      ', callback_data = get_selected_folder_name(message.chat.id))
        keyboard_markup.row(back_btn)
        await message.reply(f'Название сэмпла "{user_data["audio_sample_name"]}" содержит недопустимые символы: {check_string_for_except_chars(audio_sample_name)}\nВведите другое имя', reply_markup=keyboard_markup)
        return 
    
    # Проверяем, существует ли аудио сэмпл с таким же названием
    if str(user_data["audio_sample_name"]).lower() in [x.lower() for x in db.select_user_audio_samples_list(message.chat.id, get_selected_folder_name(message.chat.id))]:
        keyboard_markup = types.InlineKeyboardMarkup()
        back_btn = types.InlineKeyboardButton('«      ', callback_data = get_selected_folder_name(message.chat.id))
        keyboard_markup.row(back_btn)
        await message.reply("Данное название аудио сэмпла уже существует, введите другое имя", reply_markup=keyboard_markup)
        return
     
    await state.finish()
    managment_msg = await message.reply('Задача поставлена в поток!')
    
    try:
        # Stage 0 : download file
        managment_msg = await download_file(managment_msg, file_id, path_list.tmp_audio_samples(audio_sample_full_name))
        # Stage 1 : check audio files for integrity and mormalize, convert them
        managment_msg = await audio_processing(managment_msg, path_list.tmp_audio_samples(audio_sample_full_name), path_list.processed_audio_samples(audio_sample_name + ".mp3"))
        # Stage 2 : analyze current audio sample hashes
        managment_msg = await register_audio_hashes(managment_msg, path_list.processed_audio_samples(audio_sample_name + ".mp3"), path_list.fingerprint_db())
        # Stage 3 : register current audio sample hashes
        db.register_audio_sample(message.chat.id, get_selected_folder_name(message.chat.id), user_data["audio_sample_name"], user_data["audio_sample_file_info"].file_unique_id)
    except Exception as ex:
        logging.exception(ex)
        keyboard_markup = types.InlineKeyboardMarkup()
        manage_folder_menu_message_btn = types.InlineKeyboardButton('« Вернутся к текущей папке', callback_data = manage_folder_cb.new(get_selected_folder_name(message.chat.id)))
        upload_sample_btn = types.InlineKeyboardButton('» Попробовать еще раз загрузить сэмпл', callback_data = upload_audio_sample_cb.new(get_selected_folder_name(message.chat.id)))
        keyboard_markup.row(manage_folder_menu_message_btn)
        keyboard_markup.row(upload_sample_btn)
        await message.reply(f'Во времмя обработки аудио сэмпла с названием "{user_data["audio_sample_name"]}" возникла ошибка', reply_markup=keyboard_markup)
    else:
        keyboard_markup = types.InlineKeyboardMarkup()
        manage_folder_menu_message_btn = types.InlineKeyboardButton('« Вернутся к текущей папке', callback_data = manage_folder_cb.new(get_selected_folder_name(message.chat.id)))
        upload_sample_btn = types.InlineKeyboardButton('» Загрузить еще один сэмпл', callback_data = upload_audio_sample_cb.new(get_selected_folder_name(message.chat.id)))
        keyboard_markup.row(manage_folder_menu_message_btn)
        keyboard_markup.row(upload_sample_btn)
        await message.reply(f'Аудио сэмпл с названием "{user_data["audio_sample_name"]}" успешно сохранён', reply_markup=keyboard_markup)
    finally:
        try:
            os.remove(path_list.tmp_audio_samples(audio_sample_full_name))
            os.remove(path_list.processed_audio_samples(audio_sample_name + ".mp3"))
        except:
            pass

@dp.callback_query_handler(remove_audio_sample_cb.filter(), state='*')
async def remove_audio_sample_message(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    folder_name = callback_data['folder_name']
    
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add("<<< Отмена >>>")
    for audio_sample_name in db.select_user_audio_samples_list(call.message.chat.id, get_selected_folder_name(call.message.chat.id)):
        keyboard.add(audio_sample_name)
    
    await call.message.delete()
    await call.message.answer("Выберите аудио сэмпл который хотите удалить:", reply_markup=keyboard)
    await RemoveSample.step_1.set()
    
@dp.message_handler(state=RemoveSample.step_1, content_types=types.ContentTypes.TEXT)
async def remove_audio_sample_step_1_message(message: types.Message, state: FSMContext):
    async with state.proxy() as user_data:
        user_data['chosen_sample'] = message.text
    await state.finish()
    path_list = path(message.chat.id, get_selected_folder_name(message.chat.id))
   
    if user_data['chosen_sample'] == "<<< Отмена >>>":
        keyboard_markup = types.InlineKeyboardMarkup()
        manage_folder_menu_message_btn = types.InlineKeyboardButton('« Вернутся к текущей папке', callback_data = manage_folder_cb.new(get_selected_folder_name(message.chat.id)))
        upload_sample_btn = types.InlineKeyboardButton('» Удалить аудио сэмпл  ', callback_data = remove_audio_sample_cb.new(get_selected_folder_name(message.chat.id)))
        keyboard_markup.row(manage_folder_menu_message_btn)
        keyboard_markup.row(upload_sample_btn)
        await message.reply('Вы отменили операцию', reply_markup=keyboard_markup)
        return 
    
    managment_msg = await message.reply('Задача поставлена в поток!')

    try:
        db.unregister_audio_sample(message.chat.id, get_selected_folder_name(message.chat.id), user_data['chosen_sample'])
        
        #if len(db.select_user_audio_samples_list(message.chat.id, get_selected_folder_name(message.chat.id))) == 1:
        #    os.remove(path_list.fingerprint_db())
        #    logging.info("Deliting fingerprint file")
        #else:
        await delete_audio_hashes(managment_msg, path_list.fingerprint_db(), path_list.processed_audio_samples(user_data['chosen_sample'] + ".mp3"))
    except Exception as ex:
        logging.exception(ex)
        keyboard_markup = types.InlineKeyboardMarkup()
        manage_folder_menu_message_btn = types.InlineKeyboardButton('« Вернутся к текущей папке', callback_data = manage_folder_cb.new(get_selected_folder_name(message.chat.id)))
        upload_sample_btn = types.InlineKeyboardButton('» Удалить еще один сэмпл  ', callback_data = remove_audio_sample_cb.new(get_selected_folder_name(message.chat.id)))
        keyboard_markup.row(manage_folder_menu_message_btn)
        keyboard_markup.row(upload_sample_btn)
        await message.reply('Извините, что-то пошло не так', reply_markup=keyboard_markup)
    else:        
        keyboard_markup = types.InlineKeyboardMarkup()
        manage_folder_menu_message_btn = types.InlineKeyboardButton('« Вернутся к текущей папке', callback_data = manage_folder_cb.new(get_selected_folder_name(message.chat.id)))
        upload_sample_btn = types.InlineKeyboardButton('» Удалить еще один сэмпл  ', callback_data = remove_audio_sample_cb.new(get_selected_folder_name(message.chat.id)))
        keyboard_markup.row(manage_folder_menu_message_btn)
        keyboard_markup.row(upload_sample_btn)
        await message.reply(f'Аудио сэмпл с названием "{user_data["chosen_sample"]}" успешно удален', reply_markup=keyboard_markup)


@dp.callback_query_handler(recognize_query_cb.filter(), state='*')
async def recognize_query_message(call: types.CallbackQuery, callback_data: dict):
    folder_name = callback_data['folder_name']
    
    keyboard_markup = types.InlineKeyboardMarkup()
    back_btn = types.InlineKeyboardButton('«      ', callback_data = manage_folder_cb.new(folder_name))
    keyboard_markup.row(back_btn)
    await call.message.edit_text(
                    f'Вы работаете с папкой "{folder_name}", в режиме викторины\n\n'
                    "<i>Жду от тебя голосовое сообщение</i>",
                    parse_mode="HTML", 
                    reply_markup=keyboard_markup)
    await UploadQuery.step_1.set()

@dp.message_handler(state=UploadQuery.step_1, content_types=types.ContentTypes.VOICE)
async def recognize_query_step_1_message(message: types.Message, state: FSMContext):
    file_id = message.voice.file_id
    path_list = path(message.chat.id, get_selected_folder_name(message.chat.id))

    if message.voice.mime_type == "audio/ogg":
        audio_sample_file_extensions =  ".ogg"
    else:
        audio_sample_file_extensions =  "NULL"
    
    random_str = generate_random_string(32)
    query_audio_full_name= f"{random_str}{audio_sample_file_extensions}"
    query_audio_name = f"{random_str}"
    
    ### Todo !
    if audio_sample_file_extensions not in ('.ogg'):
        await message.reply('Что-то пошло не так. Код ошибки : mime_query_audio_error')
        await folder_list_menu_message(message, 'start')
        return
    
    await state.finish()
    managment_msg = await message.reply('Задача поставлена в поток!')
    
    try:
        # Stage 0 : download file
        managment_msg = await download_file(managment_msg, file_id, path_list.tmp_query_audio(query_audio_full_name))
        # Stage 1 : check audio files for integrity and mormalize, convert them
        managment_msg = await audio_processing(managment_msg, path_list.tmp_query_audio(query_audio_full_name), path_list.processed_query_audio(query_audio_name + ".mp3"))
        # Stage 2 : match audio query
        managment_msg = await match_audio_query(managment_msg, path_list.processed_query_audio(query_audio_name + ".mp3"), path_list.fingerprint_db())
    except:
        await folder_list_menu_message(message, 'start')
        return
    else:
        keyboard_markup = types.InlineKeyboardMarkup()
        manage_folder_menu_message_btn = types.InlineKeyboardButton('« Вернутся к текущей папке  ', callback_data=manage_folder_cb.new(get_selected_folder_name(message.chat.id)))
        upload_sample_btn = types.InlineKeyboardButton('» Распознать еще одну запись', callback_data=recognize_query_cb.new(get_selected_folder_name(message.chat.id)))
        keyboard_markup.row(manage_folder_menu_message_btn)
        keyboard_markup.row(upload_sample_btn)
        await message.reply('Аудио запись распознана', reply_markup=keyboard_markup)
    finally:
        try:
            os.remove(path_list.tmp_query_audio(query_audio_full_name))
            os.remove(path_list.processed_query_audio(query_audio_name + ".mp3"))
        except:
            pass
        
#@dp.message_handler(lambda message: message.text == "Отмена")
#async def action_cancel(message: types.Message):
#    remove_keyboard = types.ReplyKeyboardRemove()
#    await message.answer("Действие отменено. Введите /start, чтобы начать заново.", reply_markup=remove_keyboard)

@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply("Напиши мне что-нибудь, и я отпрпавлю этот текст тебе в ответ!")

@dp.errors_handler(exception=BotBlocked)
async def error_bot_blocked(update: types.Update, exception: BotBlocked):
    logging.warning(f"Меня заблокировал пользователь!\nСообщение: {update}\nОшибка: {exception}")
    return True

@dp.errors_handler(exception=MessageNotModified)
async def message_not_modified_handler(update: types.Update, exception: BotBlocked):
    return True

@dp.message_handler(content_types=types.ContentType.ANY, state='*')
async def unknown_message(msg: types.Message):
    await msg.reply('Я не знаю, что с этим делать\nЯ просто напомню, что есть команда /help', parse_mode="HTML")

@dp.callback_query_handler(state='*')
async def callback_handler(query: types.CallbackQuery, state):
    answer_data = query.data
    if answer_data == 'welcome_message':
        await query.answer()
        await main_menu_message(query.message, 'edit')
    if answer_data == 'edit_lang':
        await query.answer()
        await language_settings_message(query.message, 'edit')
    if answer_data == 'folders_list':
        await state.finish()
        await query.answer()
        await folder_list_menu_message(query.message, 'edit')
    if answer_data == 'create_new_folder':
        if int(db.user_folders_count(query.message.chat.id)) > 10:
            await query.answer('Список папок превышает 10 папок', True)
            return
        await query.answer()
        await create_folder_step_1_message(query.message)
#    if answer_data == 'folder_delete':
#        await query.answer()
#        await delete_folder_step_1_message(query.message)
#    if answer_data == 'upload_audio_samples':
#        if len(db.select_user_audio_samples_list(query.message.chat.id, get_selected_folder_name(query.message.chat.id))) > 90:
#            await query.answer('Список аудио сэмплов превышает 90 сэмплов', True)
#            return 
#        await query.answer()
#        await upload_audio_sample_message(query.message)
#    if answer_data == 'remove_audio_samples':
#        if len(db.select_user_audio_samples_list(query.message.chat.id, get_selected_folder_name(query.message.chat.id))) == 0:
#            await query.answer('У вас нету аудио сэмлов', True)
#            return
#        await query.answer()
#        await remove_audio_sample_message(query.message)
#    if answer_data == 'quiz_mode_0':
#        if len(db.select_user_folders_list(query.message.chat.id)) == 0:
#            await query.answer('У Вас нету папок', True)
#            return
#        await query.answer()
#        await quiz_mode_step_0(query.message)
#    if answer_data == 'quiz_mode_1':
#        if len(db.select_user_audio_samples_list(query.message.chat.id, get_selected_folder_name(query.message.chat.id))) == 0:
#            await query.answer(f'В папке "{get_selected_folder_name(query.message.chat.id)}" нету аудио сэмлов', True)
#            return
#        await query.answer()
#        await quiz_mode_step_1(query.message)
#    for w in db.select_user_folders_list(query.message.chat.id):
#        # Fixme
#        if answer_data == "set_" + w:
#            set_selected_folder_name(query.message.chat.id, str(w))
#            if len(db.select_user_audio_samples_list(query.message.chat.id, get_selected_folder_name(query.message.chat.id))) == 0:
#                await query.answer(f'В папке "{get_selected_folder_name(query.message.chat.id)}" нету аудио сэмлов', True)
#                return
#            await query.answer()
#            await quiz_mode_step_1(query.message, "quiz_mode_step_0")
            
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
