""" PyDejavuBot
Бот-помощник для решения музыкальных викторин. Бот написан на aiogram.

/start - открыть глааное меню
"""

##Region ### START imports section ###
from database import  SQLighter
import re
import config
import logging
import asyncio
from aiogram.utils.exceptions import BotBlocked
from aiogram.utils.markdown import text, bold, italic, code, pre
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext # for using FSM
#import sqlite3 # for working with DB
import os
import os.path # need for extract extions of file
import shutil
import subprocess
import sys
#import json
from aiogram.contrib.fsm_storage.memory import MemoryStorage
##EndRegion ### END imports section ###

API_TOKEN = config.API_TOKEN # Initalialization API token for work with Telegram Bot

#ConfigureMemoryStorage
memory_storage = MemoryStorage()
# Configure logging
logging.basicConfig(level=logging.INFO)
#logging.basicConfig(level=logging.DEBUG) 

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=memory_storage)

class Create_Folders(StatesGroup):
    create_new_folder_step_1 = State()
    create_new_folder_step_2 = State()
class Upload_Simples(StatesGroup):
    upload_audio_samples_step_1 = State()
    upload_audio_samples_step_2 = State()
    upload_audio_samples_step_3 = State()
class Remove_Simples(StatesGroup):
    remove_audio_samples_step_1 = State()
    remove_audio_samples_step_2 = State()
    
class get_path:
    def __init__(self, user_id, user_folder):
        self.user_id = user_id
        self.select_user_folder = user_folder
    def tmp_audio_samples(self, file = ""):
        return f'data/audio_samples/tmp/{self.user_id}/{self.select_user_folder}/{file}'
    def non_normalized_audio_samples(self, file = ""):
        return f'data/audio_samples/non_normalized/{self.user_id}/{self.select_user_folder}/{file}'
    def normalized_audio_samples(self, file = ""):
        return f'data/audio_samples/normalized/{self.user_id}/{self.select_user_folder}/{file}'
    def fingerprint_db(self):
        return f'data/audio_samples/fingerprint_db/{self.user_id}/{self.select_user_folder}.fpdb'
    def fingerprint_db_dir_path(self):
        return f'data/audio_samples/fingerprint_db/{self.user_id}/'

def b_get_text_in_lang(data):
	lang_type = "En"
	dict_miltilang = {
	    '1' : {'Ru' : '🎛️ Настройки : Выбран русский язык 🇷🇺',
	             'En' : "🎛️ Setings : Selected English 🇺🇸 language!"},
	    '2' : {'Ru' : 'Настройки ⚙️',
	             'En' : 'Settings ⚙️'}
	}
	return dict_miltilang[data][lang_type]

curent_folder_name = {}

def get_selected_folder_name(user_id):
    global curent_folder_name
    return curent_folder_name[user_id]

def set_selected_folder_name(user_id, set_name):
    global curent_folder_name
    curent_folder_name[user_id] = set_name
    
##Region ### START backends section ###
def get_user_folders_list(user_id):
    db_worker = SQLighter(config.database_name)
    db_data = db_worker.select_user_folders_list(user_id)
    db_worker.close()
    return db_data
    
def get_user_folders_count(user_id):
    db_worker = SQLighter(config.database_name)
    db_data = db_worker.select_user_folders_count(user_id)
    db_worker.close()
    return db_data

def get_user_data(user_id):
    db_worker = SQLighter(config.database_name)
    db_data = db_worker.select_user_data(user_id)
    db_worker.close()
    return db_data

def check_name_for_except_chars(string):
    exception_chars = '\\\/\|<>\?:"\*'
    find_exceptions = re.compile('([{}])'.format(exception_chars))
    return find_exceptions.findall(string)
    
async def check_audio_integrity_and_convert(message, input_file, output_file):
    message_text = message.text + "\n\nПроверка аудио файла на целостность и конвертируем в формат mp3 через ffmpeg..."
    await message.edit_text(message_text + " Выполняем...")
    args = ['ffmpeg', '-hide_banner', '-loglevel', 'warning', '-i', input_file, output_file]; print(args)
    process = subprocess.Popen(args, stdout=subprocess.PIPE,  stderr=subprocess.PIPE, encoding='utf-8')
    data = process.communicate()
    if data[1] == "":
        managment_msg = await message.edit_text(message_text + " Готово ✅")
        return True, managment_msg
    else:
        message_text += "\nОбнаружены ошибки ffmpeg:\n" + code(f"{data[1]}\n") 
        managment_msg = await message.edit_text(message_text, parse_mode=types.ParseMode.MARKDOWN)
        if os.path.exists(output_file) is False:
            managment_msg = await message.edit_text(message_text + text("Критическая ошибка, файл отсутсвует, выходим..."), parse_mode=types.ParseMode.MARKDOWN)
            return False, managment_msg
        return True, managment_msg

async def normalize_audio(message, input_file, output_file):
    message_text = message.text + "\n\nНормализуем аудио..."
    await message.edit_text(message_text + " Выполняем...")
    args = ['ffmpeg-normalize', '-q', input_file, '-c:a', 'libmp3lame', '-o', output_file]; print(args)
    process = subprocess.Popen(args, stdout=subprocess.PIPE,  stderr=subprocess.PIPE, encoding='utf-8')
    data = process.communicate()
    if data[1] == "":
        managment_msg = await message.edit_text(message_text + " Готово ✅")
        return True, managment_msg
    else:
        message_text += "\nОбнаружены ошибки:\n" + code(f"{data[1]}\n") 
        managment_msg = await message.edit_text(message_text, parse_mode=types.ParseMode.MARKDOWN)
        if os.path.exists(output_file) is False:
            managment_msg = await message.edit_text(message_text + text("Критическая ошибка, файл отсутсвует, выходим..."), parse_mode=types.ParseMode.MARKDOWN)
            return False, managment_msg
        return True, managment_msg

async def analyze_audio_sample(message, input_file, fingerprint_db):
    message_text = message.text + "\n\nРегистрируем аудио хэшов в базу данных..."
    await message.edit_text(message_text + " Выполняем...")
    ### -n 500 -H 2 -F 20 -h 40
    if os.path.exists(fingerprint_db) is False:
        db_hashes_add_method = 'new'
    elif os.path.exists(fingerprint_db) is True:
        db_hashes_add_method = 'add'
    args = ['python3', 'library/audfprint-master/audfprint.py', db_hashes_add_method, '-d', fingerprint_db, input_file]; print(args)
    process = subprocess.Popen(args, stdout=subprocess.PIPE,  stderr=subprocess.PIPE, encoding='utf-8')
    data = process.communicate()
    if data[1] == "":
        managment_msg = await message.edit_text(message_text + " Готово ✅")
        return True, managment_msg
    else:
        message_text += "\nОбнаружены ошибки:\n" + code(f"{data[1]}\n") 
        managment_msg = await message.edit_text(message_text, parse_mode=types.ParseMode.MARKDOWN)
        return True, managment_msg

async def delete_audio_hashes(fingerprint_db, sample_name):
    args = ['python3', 'library/audfprint-master/audfprint.py', 'remove', '-d', fingerprint_db, sample_name]; print(args)
    process = subprocess.Popen(args, stdout=subprocess.PIPE,  stderr=subprocess.PIPE, encoding='utf-8')
    data = process.communicate()

##EndRegion ### END backends section ###
@dp.message_handler(commands=['start'], state='*')
async def send_welcome(message: types.Message):
    if get_user_data(message.chat.id) is None:
        db_worker = SQLighter(config.database_name)
        db_worker.create_empety_user_data(message.chat.id)
        db_worker.close()
    db_worker = SQLighter(config.database_name)
    get_lang = db_worker.get_lang(message.chat.id)
    db_worker.close()
    if get_lang == '':
        await f_set_lang(message, 'start')
    else:
        await f_welcome_message(message, 'reply')

@dp.callback_query_handler(lambda c: c.data == 'bot_settings')
async def bot_settings(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    keyboard_markup = types.InlineKeyboardMarkup()
    back_btn = types.InlineKeyboardButton('«      ', callback_data= 'welcome_message')
    lang_btn = types.InlineKeyboardButton(f'Язык : {get_user_data(callback_query.message.chat.id)[1]}', callback_data= 'edit_lang')
    keyboard_markup.row(back_btn,lang_btn)
    await callback_query.message.edit_text("Настройки бота:", reply_markup=keyboard_markup)

@dp.callback_query_handler(lambda c: c.data == 'about_bot')
async def about_bot(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    keyboard_markup = types.InlineKeyboardMarkup()
    back_btn = types.InlineKeyboardButton('«      ', callback_data= 'welcome_message')
    keyboard_markup.row(back_btn)
    text = """ LenDejavuBot - бот предназначенный для решения музыкальных викторин. Бот специально разработан для Павлодарского музыкального колледжа\n
Разработчик ботка : @Zhymabek_Roman
Тех.поддержка : @Zhymabek_Roman"""
    await callback_query.message.edit_text(text, reply_markup=keyboard_markup)
    
async def quiz_mode_step_0(message: types.Message):
    keyboard_markup = types.InlineKeyboardMarkup()
    for folder_name in get_user_folders_list(message.chat.id):
        get_sample_count = len(get_user_folders_list(message.chat.id)[folder_name])
        folder_btn = types.InlineKeyboardButton(f"{folder_name} ({get_sample_count})", callback_data= folder_name)
        keyboard_markup.row(folder_btn)
    back_btn = types.InlineKeyboardButton('«      ', callback_data= 'welcome_message')
    keyboard_markup.row(back_btn)
    await message.edit_text("Выберите папку : ", reply_markup=keyboard_markup)   
    await Create_Folders.create_new_folder_step_2.set()

async def f_welcome_message(message: types.Message, type_start):
    keyboard_markup = types.InlineKeyboardMarkup()
    folder_list_btns = types.InlineKeyboardButton('Папки 📂', callback_data= 'folders_list')
    about_btns = types.InlineKeyboardButton('О боте 🤖', callback_data= 'about_bot')
    setings_btns = types.InlineKeyboardButton('Настройки  🎛️', callback_data= 'bot_settings')
    quiz_mode_btn = types.InlineKeyboardButton('Режим Викторины', callback_data= 'quiz_mode_0')
    keyboard_markup.row(folder_list_btns)
    keyboard_markup.row(about_btns, setings_btns)
    keyboard_markup.row(quiz_mode_btn)
    if type_start == 'edit':
        await message.edit_text("Меню : ", reply_markup=keyboard_markup)
    elif type_start == 'reply':
        await message.reply("Меню : ", reply_markup=keyboard_markup)

async def f_set_lang(message : types.Message, type_start= 'start' ):
    keyboard_markup = types.InlineKeyboardMarkup()
    set_en_lang_btns = types.InlineKeyboardButton('English 🇺🇸', callback_data= 'set_lang-en')
    set_ru_lang_btns = types.InlineKeyboardButton('Russian 🇷🇺', callback_data= 'set_lang-ru')
    set_kz_lang_btns = types.InlineKeyboardButton('Kazakh 🇰🇿', callback_data= 'set_lang-kz')
    keyboard_markup.row(set_ru_lang_btns, set_en_lang_btns, set_kz_lang_btns)
    if type_start == 'start':
        await message.reply("Please select your language:", reply_markup=keyboard_markup)
    elif type_start == 'edit':
        await message.edit_text("Please select your language:", reply_markup=keyboard_markup)

async def f_folder_list(message : types.Message, type_start):
    set_selected_folder_name(message.chat.id, "")
    keyboard_markup = types.InlineKeyboardMarkup()
    create_new_folder_btn = types.InlineKeyboardButton('Создать новую папку 🗂', callback_data= 'create_new_folder')
    keyboard_markup.row(create_new_folder_btn)
    
    for folder_name in get_user_folders_list(message.chat.id):
        get_sample_count = len(get_user_folders_list(message.chat.id)[folder_name])
        folder_btn = types.InlineKeyboardButton(f"{folder_name} ({get_sample_count})", callback_data= folder_name)
        keyboard_markup.row(folder_btn)
 
    back_btn = types.InlineKeyboardButton('«      ', callback_data= 'welcome_message')
    keyboard_markup.row(back_btn)
    if type_start == 'start':
        await message.answer("Менеджер папок\n\nОбщее количество папок: {0}".format(get_user_folders_count(message.chat.id)), reply_markup=keyboard_markup)
    elif type_start == 'edit':
        await message.edit_text("Менеджер папок\n\nОбщее количество папок: {0}".format(get_user_folders_count(message.chat.id)), reply_markup=keyboard_markup)
    
@dp.message_handler(state = Create_Folders.create_new_folder_step_1, content_types=types.ContentTypes.TEXT)
async def f_create_new_folder_step_1(message: types.Message):
    keyboard_markup = types.InlineKeyboardMarkup()
    back_btn = types.InlineKeyboardButton('«      ', callback_data= 'folders_list')
    keyboard_markup.row(back_btn)
    await message.edit_text("Введите название вашей папки : ", reply_markup=keyboard_markup)   
    await Create_Folders.create_new_folder_step_2.set()

@dp.message_handler(state = Create_Folders.create_new_folder_step_2, content_types=types.ContentTypes.TEXT)
async def f_create_new_folder_step_2(message: types.Message, state: FSMContext):
    await state.update_data(folder_name=message.text)
    user_data = await state.get_data()
    
    if len(user_data['folder_name']) >=  10:
        await message.reply('Название папки превышает 10 символов')
        return
        
    for x in get_user_folders_list(message.chat.id):
        if x.lower() == user_data['folder_name'].lower():
            await message.reply('Данная папка уже существует! Введите другое имя')
            return

    if check_name_for_except_chars(user_data['folder_name']):
        await message.reply('Название папки "{}" содержит недопустимые символы: {}'.format(user_data['folder_name'], check_name_for_except_chars(user_data['folder_name'])))
        return 
    
    path_list = get_path(message.chat.id, user_data['folder_name'])
    os.makedirs(path_list.tmp_audio_samples())
    os.makedirs(path_list.non_normalized_audio_samples())
    os.makedirs(path_list.normalized_audio_samples())
    try:
        os.makedirs(path_list.fingerprint_db_dir_path())
    except:
        pass
    db_worker = SQLighter(config.database_name)
    db_worker.create_folder(message.chat.id, user_data['folder_name'])
    db_worker.close()
    await message.reply(f"Папка {user_data['folder_name']} создана!")
    await f_folder_list(message, 'start') 
    await state.finish()
        
async def manage_folder(message, folder_name):
    set_selected_folder_name(message.chat.id, folder_name)
    
    keyboard_markup = types.InlineKeyboardMarkup()
    delete_btn = types.InlineKeyboardButton('Удалить папкy 🗑', callback_data= 'folder_delete')
    keyboard_markup.row(delete_btn)
    upload_audio_samples_btn = types.InlineKeyboardButton('Загрузить аудио сэмплы', callback_data= 'upload_audio_samples')
    keyboard_markup.row(upload_audio_samples_btn)
    remove_audio_samples_btn = types.InlineKeyboardButton('Удалить аудио сэмплы', callback_data= 'remove_audio_samples')
    keyboard_markup.row(remove_audio_samples_btn)
    quiz_mode_btn = types.InlineKeyboardButton('Режим Викторины', callback_data= 'quiz_mode')
    keyboard_markup.row(quiz_mode_btn)
    back_btn = types.InlineKeyboardButton('«      ', callback_data= 'folders_list')
    keyboard_markup.row(back_btn)
    
    samples_name = ""
    for i, b in enumerate(get_user_folders_list(message.chat.id)[get_selected_folder_name(message.chat.id)], 1):
        samples_name += str(f"{i}) {b}\n")
    
    await message.edit_text("Вы работаете с папкой : " + str(get_selected_folder_name(message.chat.id)) + "\n" + "\n" + 
                        "Список аудио сэмлов : \n" + samples_name
                        + "\n"+ "Ваши действия - ", reply_markup=keyboard_markup)

async def f_delete_folder_step_1(message):
    keyboard_markup = types.InlineKeyboardMarkup()
    delete_btn = types.InlineKeyboardButton('Да!', callback_data= 'process_to_delete_folder')
    back_btn = types.InlineKeyboardButton('«      ', callback_data= 'folders_list')
    keyboard_markup.row(delete_btn)
    keyboard_markup.row(back_btn)
    await message.edit_text(f"Вы действительно хотите удалить папку {get_selected_folder_name(message.chat.id)}?\nЭТО ДЕЙСТВИЕ НЕЛЬЗЯ ОТМЕНИТЬ!", reply_markup=keyboard_markup)

@dp.callback_query_handler(lambda c: c.data == 'process_to_delete_folder')
async def f_delete_folder_step_2(callback_query: types.CallbackQuery):
    path_list = get_path(callback_query.message.chat.id, get_selected_folder_name(callback_query.message.chat.id))
    shutil.rmtree(path_list.tmp_audio_samples())
    shutil.rmtree(path_list.non_normalized_audio_samples())
    shutil.rmtree(path_list.normalized_audio_samples())
    try:
        shutil.rmtree(path_list.fingerprint_db())
    except:
        pass
    db_worker = SQLighter(config.database_name)
    db_worker.unregister_all_audio_sample(callback_query.message.chat.id, get_selected_folder_name(callback_query.message.chat.id))
    db_worker.delete_folder(callback_query.message.chat.id, get_selected_folder_name(callback_query.message.chat.id))
    db_worker.close()

    await callback_query.message.edit_text(f"Папка {get_selected_folder_name(callback_query.message.chat.id)} удалена!")
    await f_folder_list(callback_query.message, 'start')
    
@dp.message_handler(state = Upload_Simples.upload_audio_samples_step_1)
async def f_upload_audio_samples_step_1(message):
    keyboard_markup = types.InlineKeyboardMarkup()
    back_btn = types.InlineKeyboardButton('«      ', callback_data= get_selected_folder_name(message.chat.id))
    keyboard_markup.row(back_btn)
    await message.edit_text(f"Вы работаете с папкой : {get_selected_folder_name(message.chat.id)}\nЖду от тебя аудио сэмплы", reply_markup=keyboard_markup)
    await Upload_Simples.upload_audio_samples_step_2.set()

@dp.message_handler(state = Upload_Simples.upload_audio_samples_step_2, content_types=types.ContentTypes.DOCUMENT | types.ContentTypes.AUDIO)
async def f_upload_audio_samples_step_2(message: types.Message, state: FSMContext):
    await state.update_data(audio_sample_message=message)
    await state.update_data(audio_sample_content_type=message.content_type)
    user_data = await state.get_data()
    if user_data["audio_sample_content_type"] == "document":
        await state.update_data(audio_sample_file_info=message.document)
        name_file = user_data["audio_sample_message"].document.file_name
        await state.update_data(audio_sample_file_extensions =  os.path.splitext(name_file)[1])
    elif user_data["audio_sample_content_type"] == "audio":
        await state.update_data(audio_sample_file_info=message.audio)
        if message.audio.mime_type == "audio/mpeg":
            await state.update_data(audio_sample_file_extensions =  ".mp3")
        elif message.audio.mime_type == "audio/x-opus+ogg":
            await state.update_data(audio_sample_file_extensions =  ".ogg")
        else:
            await state.update_data(audio_sample_file_extensions =  "NULL")
    user_data = await state.get_data()
    if user_data["audio_sample_file_extensions"] in ('.wav', '.mp3', '.wma', '.ogg'):
        keyboard_markup = types.InlineKeyboardMarkup()
        back_btn = types.InlineKeyboardButton('«      ', callback_data= 'folders_list')
        keyboard_markup.row(back_btn)
        await message.reply("Введите название вашей аудио записи : ", reply_markup=keyboard_markup)
        await Upload_Simples.upload_audio_samples_step_3.set()
    else:
        await message.reply('Мы такой формат не принемаем, пришлите в другом формате\nИзвините за неудобства!')
        return

@dp.message_handler(state= Upload_Simples.upload_audio_samples_step_3, content_types=types.ContentTypes.TEXT)
async def f_upload_audio_samples_step_3(message: types.Message, state: FSMContext):
    await state.update_data(audio_sample_name=message.text)
    user_data = await state.get_data()
    file_id = user_data["audio_sample_file_info"].file_id
    audio_sample_name = f'{user_data["audio_sample_name"]}'
    audio_sample_full_name = f'{user_data["audio_sample_name"]}{user_data["audio_sample_file_extensions"]}'
    path_list = get_path(message.chat.id, get_selected_folder_name(message.chat.id))
    
    if len(str(user_data["audio_sample_name"])) >= 50:
        await message.reply('Название файла превышает 50 символов')
        return
    
    if check_name_for_except_chars(user_data["audio_sample_name"]):
        await message.reply('Название папки "{}" содержит недопустимые символы: {}'.format(user_data["audio_sample_name"], check_name_for_except_chars(audio_sample_name)))
        return 
    
    for  x in get_user_folders_list (message.chat.id)[get_selected_folder_name(message.chat.id)]:
        if str(user_data["audio_sample_name"]).lower() == str(x).lower():
            await message.reply("Данная запись уже существует, введите другое имя : ")
            return
     
    managment_msg = await message.reply('Загрузка файла... Подождите...')
    await bot.download_file_by_id(file_id=file_id, destination = path_list.tmp_audio_samples(audio_sample_full_name)); await asyncio.sleep(1)
    managment_msg = await managment_msg.edit_text("Загрузка файла... Готово ✅")
    
    # Stage 1 : check audio files for integrity and convert them
    ffmpeg_status, managment_msg = await check_audio_integrity_and_convert(managment_msg, path_list.tmp_audio_samples(audio_sample_full_name), path_list.non_normalized_audio_samples(audio_sample_name + ".mp3"))
    if ffmpeg_status is False:
        #os.remove(out_file) ### TODO Remove trash files 
        await state.finish()
        await f_folder_list(message, 'start') 
        return
    
    # Stage 2 : mormalize audio
    ffmpeg_normalizing_status, managment_msg = await normalize_audio(managment_msg, path_list.non_normalized_audio_samples(audio_sample_name + ".mp3"), path_list.normalized_audio_samples(audio_sample_name + ".mp3"))
    if ffmpeg_normalizing_status is False:
        await state.finish()
        await f_folder_list(message, 'start') 
        return
    
    # Stage 3 : register current audio sample hashes
    audfprint_status, managment_msg = await analyze_audio_sample(managment_msg, path_list.normalized_audio_samples(audio_sample_name + ".mp3"), path_list.fingerprint_db())
    if audfprint_status is False:
        await state.finish()
        await f_folder_list(message, 'start') 
        return
        
    db_worker = SQLighter(config.database_name)
    db_worker.register_audio_sample(message.chat.id, get_selected_folder_name(message.chat.id), user_data["audio_sample_name"], file_id)
    db_worker.close()
    
    await message.reply(f'Файл с названием {user_data["audio_sample_name"]} успешно сохранён')
    await state.finish()
    await f_folder_list(message, 'start') 

@dp.message_handler(state= Remove_Simples.remove_audio_samples_step_1)
async def f_remove_audio_samples_step_1(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    
    keyboard.add("<<< Отмена >>>")
    for i in get_user_folders_list(message.chat.id)[get_selected_folder_name(message.chat.id)]:
        keyboard.add(str(i))
    keyboard.add("<<< Отмена >>>")
    
    await message.edit_text(f"Количество аудио сэмлов в этой папке : {len(get_user_folders_list(message.chat.id)[get_selected_folder_name(message.chat.id)])}")
    await message.answer("Выберите аудио сэмпл который хотите удалить:", reply_markup=keyboard)
    await Remove_Simples.remove_audio_samples_step_2.set()
    
@dp.message_handler(state= Remove_Simples.remove_audio_samples_step_2, content_types=types.ContentTypes.TEXT)
async def f_remove_audio_samples_step_2(message: types.Message, state: FSMContext):
    await state.update_data(chosen_sample=message.text)
    user_data = await state.get_data()
    path_list = get_path(message.chat.id, get_selected_folder_name(message.chat.id))
    if user_data['chosen_sample'] == "<<< Отмена >>>":
        logging.info("<<< Отмена >>>")
        await message.reply("Вы отменили операцию", reply_markup=types.ReplyKeyboardRemove())
        await state.finish()
        await f_folder_list(message, 'start') 
        return 
    try:
        db_worker = SQLighter(config.database_name)
        db_worker.unregister_audio_sample(message.chat.id, get_selected_folder_name(message.chat.id), user_data['chosen_sample'])
        db_worker.close()
    except KeyError:
        await message.reply("Такого аудио сэмпла нету. Выходим ...", reply_markup=types.ReplyKeyboardRemove())
        await state.finish()
        await f_folder_list(message, 'start') 
        return
    managment_msg = await message.reply(f"Сэмпл {user_data['chosen_sample']} в процесе удаления ...", reply_markup=types.ReplyKeyboardRemove()) 
    await delete_audio_hashes(path_list.fingerprint_db(), path_list.normalized_audio_samples(user_data['chosen_sample'] + ".mp3"))
#    await bot.edit_message_text(chat_id=managment_msg.chat.id, message_id=managment_msg.message_id, text= f"Сэмпл {user_data['chosen_sample']} успешно удален.")
    await state.finish()
    await f_folder_list(message, 'start') 
    
@dp.message_handler(lambda message: message.text == "Отмена")
async def action_cancel(message: types.Message):
    remove_keyboard = types.ReplyKeyboardRemove()
    await message.answer("Действие отменено. Введите /start, чтобы начать заново.", reply_markup=remove_keyboard)

@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply("Напиши мне что-нибудь, и я отпрпавлю этот текст тебе в ответ!")

@dp.message_handler(commands=['stop'])
async def stop(message: types.Message):
    await message.reply("Бот остановлен!")
    sys.exit()
    
@dp.errors_handler(exception=BotBlocked)
async def error_bot_blocked(update: types.Update, exception: BotBlocked):
    print(f"Меня заблокировал пользователь!\nСообщение: {update}\nОшибка: {exception}")
    return True

@dp.message_handler(content_types=types.ContentType.ANY)
async def unknown_message(msg: types.Message):
    await msg.reply('Я не знаю, что с этим делать\nЯ просто напомню, что есть команда /help', parse_mode=types.ParseMode.MARKDOWN)

@dp.callback_query_handler(state='*')
async def callback_handler(query: types.CallbackQuery, state):
    answer_data = query.data
    if answer_data == 'welcome_message':
        await query.answer()
        await f_welcome_message(query.message, 'edit')
    if answer_data == 'set_lang-ru':
        db_worker = SQLighter(config.database_name)
        db_worker.set_lang(query.message.chat.id, "Ru")
        db_worker.close()
        await query.answer('🎚Настройки : Выбран русский язык 🇷🇺')
        await f_welcome_message(query.message, 'edit')
    if answer_data == 'set_lang-en':
        await query.answer('Бот в процесе разработки. В данное время поддерживается только русскии язык', True)
#        await query.answer('️🎚Setings : Selected English 🇺🇸 language!')
#        await f_welcome_message(query.message, 'edit')
    if answer_data == 'set_lang-kz':
        await query.answer('Бот в процесе разработки. В данное время поддерживается только русскии язык', True)
#        await query.answer('️🎚Setings : Selected Kazakh 🇰🇿 language!')
#        await f_welcome_message(query.message, 'edit')
    if answer_data == 'edit_lang':
        await query.answer()
        await f_set_lang(query.message, 'edit')
    if answer_data == 'folders_list':
        await state.finish()
        await query.answer()
        await f_folder_list(query.message, 'edit')
    if answer_data == 'create_new_folder':
        if int(get_user_folders_count(query.message.chat.id)) < 7:
            await query.answer()
            await f_create_new_folder_step_1(query.message)
        else:
            await query.answer('Список папок превышает 7 папок', True)
    if answer_data == 'folder_delete':
        await query.answer()
        await f_delete_folder_step_1(query.message)
    if answer_data == 'upload_audio_samples':
        await query.answer()
        await f_upload_audio_samples_step_1(query.message)
    if answer_data == 'remove_audio_samples':
        if len(get_user_folders_list(query.message.chat.id)[get_selected_folder_name(query.message.chat.id)]) == 0:
            await query.answer('У вас нету аудио сэмлов', True)
            return
        await query.answer()
        await f_remove_audio_samples_step_1(query.message)
    if answer_data == 'quiz_mode_0':
        await query.answer()
        await quiz_mode_step_0(query.message)
#    if answer_data == 'process_to_delete_folder':
#        await f_delete_folder_step_2(query.message)
    for w in get_user_folders_list(query.message.chat.id):
        if answer_data == w:
            await state.finish()
            await query.answer()
            await manage_folder(query.message, str(w))

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
