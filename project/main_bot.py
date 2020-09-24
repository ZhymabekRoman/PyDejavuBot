""" PyDejavuBot
Бот-помощник для решения музыкальных викторин. Бот написан на aiogram.

/start - открыть глааное меню
"""


##Region ### START imports section ###
#from threading import Thread  #for using thread
import config
from collections import defaultdict
#import time
import logging
import asyncio
from aiogram.utils.exceptions import BotBlocked
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext # for using FSM
import sqlite3 # for working with DB
import os.path # need for extract extions of file
import json #нужен для работы с json-кодированными данными
import password_generate # фнукции для генерации паролей
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
    create_new_folder_step_2 = State()
class Upload_Simples(StatesGroup):
    upload_audio_samples_step_2 = State()
    upload_audio_samples_step_3 = State()
class Remove_Simples(StatesGroup):
    remove_audio_samples_step_2 = State()

#initialize global vars for acces from anywhere
def cache_update_curent_user_folders():
    try:
        global curent_user_folders
        curent_user_folders = b_get_user_folders_list_with_keys(curent_user_id)
    except:
    	curent_user_folders = "None"
def cache_update_curent_folder_name(folder_name):
    global curent_folder_name
    curent_folder_name = folder_name
def cache_update_curent_user_id(msg):
    global curent_user_id
    curent_user_id = msg.chat.id
def cache_update_query_global():
    global query_global
    query_global = types.CallbackQuery

def merge_two_dicts(x, y):
    """Given two dictionaries, merge them into a new dict as a shallow copy."""
    z = x.copy()
    z.update(y)
    return z
    
##Region ### START backends section ###
def b_get_user_folders_list_with_keys(user_id):
    return json.loads(b_get_user_data(user_id)[2]) #расшифровывем json кодированные данные

def b_get_user_folders_list_with_keys_in_low_case(user_id):
    return dict((k.lower(), v) for k, v in  json.loads(b_get_user_data(user_id)[2]).items())

def b_get_user_folders_count(user_id):
    return  len(b_get_user_folders_list_with_keys(user_id))

#def b_get_user_folder_data_by_key(user_id):
#    get_curent_folders_key = b_get_user_folders_list_with_keys(user_id)[curent_folder_name] 
#    con = sqlite3.connect('myTable.db', check_same_thread=False)
#    cur = con.cursor()
#    cur.execute("SELECT * FROM projects Where project_id = '{0}'".format(get_curent_folders_key))
#    out = cur.fetchall()
#    con.close()
#    return out[0]

def b_get_user_data(user_id):
    con = sqlite3.connect('myTable.db', check_same_thread=False)
    cur = con.cursor()
    cur.execute("SELECT * FROM users Where user_id= '{0}'".format(user_id))
    con = sqlite3.connect('myTable.db', check_same_thread=False)
    out = cur.fetchone()
    con.close()
    print(out)
    return out
        
def b_delete_folder(user_id, folder_name):
    b_delete_all_audio_sample_from_folder(curent_folder_name)
    
    get_projects = b_get_user_folders_list_with_keys(user_id)
    for proj_name, proj_id in get_projects.items():
        if  proj_name == folder_name:
            print(proj_id)
            con = sqlite3.connect('myTable.db', check_same_thread=False)
            cur = con.cursor()
            cur.execute("DELETE FROM projects WHERE project_id = '{0}'".format(proj_id))
            con.commit()
            con.close()
    del get_projects[folder_name]
    data_to_add = json.dumps(get_projects)
    con = sqlite3.connect('myTable.db', check_same_thread=False)
    cur = con.cursor()
    cur.execute("UPDATE users SET projects =  '{0}' WHERE User_id = '{1}'".format(data_to_add, user_id))
    con.commit()
    con.close()
    cache_update_curent_user_folders()
    
def b_set_lang(user_id, lang_name):
    if b_get_user_data(user_id) is None: #если текущии юзер не будет найден в db, тoгда...
        con = sqlite3.connect('myTable.db', check_same_thread=False)
        cur = con.cursor()
        cur.execute("INSERT INTO users VALUES ('{0}', '{1}', '{2}')".format(user_id, lang_name, '{}'))
        con.commit()
        con.close()
    elif str(b_get_user_data(user_id)[0]) == str(user_id): #если текущии юзер найден в db, тогда....
        con = sqlite3.connect('myTable.db', check_same_thread=False)
        cur = con.cursor()
        cur.execute("UPDATE users SET Lang = '{0}' WHERE User_id = '{1}'".format(lang_name, user_id))
        con.commit()
        con.close()

def b_reg_new_folder(folder_name):
    new_data = {}
    new_data[folder_name] = {}
    get_projects = b_get_user_folders_list_with_keys(curent_user_id)
    data_to_add = json.dumps(merge_two_dicts(get_projects, new_data))
    con = sqlite3.connect('myTable.db', check_same_thread=False)
    cur = con.cursor()
    cur.execute("UPDATE users SET projects =  '{0}' WHERE User_id = '{1}'".format(data_to_add, curent_user_id))
    con.commit()
    con.close()
    cache_update_curent_user_folders()
    
def b_reg_new_audio_sample(folder_name, sample_name, file_id):
    abc = b_get_user_folders_list_with_keys(curent_user_id) # {'Djxhhx' : {'lllpl' : 'fuuff'}, 'Jdjdjd' : {}}
    new_data = {}
    new_data[sample_name] = file_id # присваевает новые значения из аргументов
    
    data_to_merge = merge_two_dicts(abc[folder_name], new_data)
    abc[folder_name] = data_to_merge
    
    data_to_add = json.dumps(abc)
    print(data_to_add)
    con = sqlite3.connect('myTable.db', check_same_thread=False)
    cur = con.cursor()
    cur.execute("UPDATE users SET projects =  '{0}' WHERE User_id = '{1}'".format(data_to_add, curent_user_id))
    con.commit()
    con.close()
    
def b_delete_all_audio_sample_from_folder(folder_name):
    abc = b_get_user_folders_list_with_keys(curent_user_id)# {'Djxhhx' : {'lllpl' : 'fuuff'}, 'Jdjdjd' : {}}
    new_data = {}
    abc[folder_name] = new_data
    print(abc)
    data_to_add = json.dumps(abc)
    print(data_to_add)
    con = sqlite3.connect('myTable.db', check_same_thread=False)
    cur = con.cursor()
    cur.execute("UPDATE users SET projects =  '{0}' WHERE User_id = '{1}'".format(data_to_add, curent_user_id))
    con.commit()
    con.close()
    
def b_delete_audio_sample(folder_name, sample_name):
    abc = b_get_user_folders_list_with_keys(curent_user_id)# {'Djxhhx' : {'lllpl' : 'fuuff'}, 'Jdjdjd' : {}}
    new_data = abc[folder_name]
    del new_data[sample_name]
    abc[folder_name] = new_data
    print(abc)
    data_to_add = json.dumps(abc)
    #print(data_to_add)
    con = sqlite3.connect('myTable.db', check_same_thread=False)
    cur = con.cursor()
    cur.execute("UPDATE users SET projects =  '{0}' WHERE User_id = '{1}'".format(data_to_add, curent_user_id))
    con.commit()
    con.close()
##EndRegion ### END backends section ###

@dp.message_handler(commands=['start'], state='*')
async def send_welcome(message: types.Message):
    cache_update_curent_user_id(message)
    cache_update_curent_user_folders()
    if b_get_user_data(curent_user_id) is None: #если текущии юзер не найден в db, тогда....
        await f_set_lang(message, 'start')
    elif str((b_get_user_data(curent_user_id))[0]) == str(curent_user_id): #если текущии юзер найден в db, тогда....
        await f_welcome_message(message, 'reply')

async def f_welcome_message(message: types.Message, type_start):
    keyboard_markup = types.InlineKeyboardMarkup()
    folder_list_btns = types.InlineKeyboardButton('Папки', callback_data= 'folders_list')
    about_btns = types.InlineKeyboardButton('О боте 🤖', callback_data= 'about_bot')
    setings_btns = types.InlineKeyboardButton('Настройки ⚙', callback_data= 'bot_settings')
    keyboard_markup.row(folder_list_btns)
    keyboard_markup.row(about_btns, setings_btns)
    if type_start == 'edit':
        await message.edit_text("Меню : ", reply_markup=keyboard_markup)
    elif type_start == 'reply':
        await message.reply("Меню : ", reply_markup=keyboard_markup)

@dp.callback_query_handler(state='*')
async def callback_handler(query: types.CallbackQuery, state):
    cache_update_curent_user_id(query.message)
    cache_update_curent_user_folders()
    cache_update_query_global()
    answer_data = query.data
    if answer_data == 'welcome_msg':
        await query.answer()
        await f_welcome_message(query.message, 'edit')
    if answer_data == 'set_lang-ru':
        await query.answer(' 🎛️ Настройки : Выбран русский язык 🇷🇺')
        b_set_lang(curent_user_id,'Ru')
        await f_welcome_message(query.message, 'edit')
    if answer_data == 'set_lang-en':
        await query.answer('🎛️ Setings : Selected English 🇺🇸 language!')
        b_set_lang(query.message.chat.id,'En')
        await f_welcome_message(query.message, 'edit')
    if answer_data == 'about_bot':
        await query.answer()
        keyboard_markup = types.InlineKeyboardMarkup()
        back_btn = types.InlineKeyboardButton('«      ', callback_data= 'welcome_msg')
        keyboard_markup.row(back_btn)
        await query.message.edit_text("Разработчик ботка : @ZhymabekRoman\nТех.поддержка : @ZhymabekRoman", reply_markup=keyboard_markup)
    if answer_data == 'bot_settings':
        await query.answer()
        keyboard_markup = types.InlineKeyboardMarkup()
        back_btn = types.InlineKeyboardButton('«      ', callback_data= 'welcome_msg')
        lang_btn = types.InlineKeyboardButton('Язык : ' + b_get_user_data(curent_user_id)[1], callback_data= 'edit_lang')
        keyboard_markup.row(back_btn,lang_btn)
        await query.message.edit_text("Настройки бота:", reply_markup=keyboard_markup)   
    if answer_data == 'edit_lang':
        await query.answer()
        await f_set_lang(query.message, 'edit')
    if answer_data == 'folders_list':
        await state.finish()
        await query.answer()
        await f_folder_list(query.message, 'edit')
    if answer_data == 'create_new_folder':
        if int(b_get_user_folders_count(curent_user_id)) < 7:
            await query.answer()
            await f_create_new_folder(query.message)
        else:
            await query.answer('Список папок превышает 7 папок', True)
    if answer_data == 'folder_delete':
        await query.answer()
        keyboard_markup = types.InlineKeyboardMarkup()
        delete_btn = types.InlineKeyboardButton('Да!', callback_data= 'process_to_delete_folder')
        keyboard_markup.row(delete_btn)
        back_btn = types.InlineKeyboardButton('«      ', callback_data= 'folders_list')
        keyboard_markup.row(back_btn)
        await query.message.edit_text("Вы действительно хотите удалить папку?\nЭТО ДЕЙСТВИЕ НЕЛЬЗЯ ОТМЕНИТЬ!", reply_markup=keyboard_markup)
    if answer_data == 'upload_audio_samples':
        await query.answer()
        await upload_audio_samples(query.message)
    if answer_data == 'remove_audio_samples':
        await query.answer()
        await remove_audio_samples(query.message)
    if answer_data == 'process_to_delete_folder':
        b_delete_folder(curent_user_id, curent_folder_name)
        await query.answer("Папка " + str(curent_folder_name) + " удалена!")
        await query.answer()
        await f_folder_list(query.message, 'edit')
    for w in range(len(curent_user_folders)):
        if answer_data == list(curent_user_folders)[w]:
            await state.finish()
            await query.answer()
            await manage_folder(query.message, str(list(curent_user_folders)[w]))
  
async def f_create_new_folder(message, type_start = 'send'):
    keyboard_markup = types.InlineKeyboardMarkup()
    back_btn = types.InlineKeyboardButton('«      ', callback_data= 'folders_list')
    keyboard_markup.row(back_btn)
    await message.edit_text("Введите название вашей папки : ", reply_markup=keyboard_markup)   
    await Create_Folders.create_new_folder_step_2.set()

@dp.message_handler(state= Create_Folders.create_new_folder_step_2, content_types=types.ContentTypes.TEXT)
async def f_create_new_folder_step_2(message: types.Message, state: FSMContext):
    if len(message.text) <=  int(10): #если длина папки будет меньше 10 символов, тогда ..... 
        for x in range(b_get_user_folders_count(curent_user_id)):
            if  list(b_get_user_folders_list_with_keys_in_low_case(curent_user_id))[x] == message.text.lower():
                #await query_global.answer('Данная папка уже существует! Введите другое имя', True)
                await message.reply('Данная папка уже существует! Введите другое имя')
                return
        b_reg_new_folder(message.text)
        #await query_global.answer("Папка " + str(message.text) + " создана!")
        await message.reply("Папка " + str(message.text) + " создана!")
        await f_folder_list(message, 'start') 
        await state.finish()
    else:
        #await query_global.answer('Название папки превышает 10 символов', True)
        await message.reply('Название папки превышает 10 символов')
        return
        
async def f_set_lang(message : types.Message, type_start= 'start' ):
    keyboard_markup = types.InlineKeyboardMarkup()
    set_en_lang_btns = types.InlineKeyboardButton('English 🇺🇸', callback_data= 'set_lang-en')
    set_ru_lang_btns = types.InlineKeyboardButton('Russian 🇷🇺', callback_data= 'set_lang-ru')
    keyboard_markup.row(set_ru_lang_btns, set_en_lang_btns)
    if type_start == 'start':
        await message.reply("Please select your language:", reply_markup=keyboard_markup)
    elif type_start == 'edit':
        await message.edit_text("Please select your language:", reply_markup=keyboard_markup)

async def f_folder_list(message : types.Message, type_start):
    keyboard_markup = types.InlineKeyboardMarkup()
    create_new_folder_btn = types.InlineKeyboardButton('Создать новую папку 🗂', callback_data= 'create_new_folder')
    keyboard_markup.row(create_new_folder_btn)
    for x in range(b_get_user_folders_count(curent_user_id)):
        folder_name = str(list(b_get_user_folders_list_with_keys(curent_user_id))[x])
        folder_btn = types.InlineKeyboardButton(folder_name, callback_data= folder_name)
        keyboard_markup.row(folder_btn)
    back_btn = types.InlineKeyboardButton('«      ', callback_data= 'welcome_msg')
    keyboard_markup.row(back_btn)
    if type_start == 'start':
        await message.answer("Менеджер папок\n\nОбщее количество папок: {0}".format(b_get_user_folders_count(curent_user_id)), reply_markup=keyboard_markup)
    elif type_start == 'edit':
        await message.edit_text("Менеджер папок\n\nОбщее количество папок: {0}".format(b_get_user_folders_count(curent_user_id)), reply_markup=keyboard_markup)
    
        
async def manage_folder(message, folder_name):
    cache_update_curent_folder_name(folder_name)
    
    keyboard_markup = types.InlineKeyboardMarkup()
    delete_btn = types.InlineKeyboardButton('Удалить папкy 🗑', callback_data= 'folder_delete')
    keyboard_markup.row(delete_btn)
    upload_audio_samples_btn = types.InlineKeyboardButton('Загрузить аудио сэмплы', callback_data= 'upload_audio_samples')
    keyboard_markup.row(upload_audio_samples_btn)
    remove_audio_samples_btn = types.InlineKeyboardButton('Удалить аудио сэмплы', callback_data= 'remove_audio_samples')
    keyboard_markup.row(remove_audio_samples_btn)
    back_btn = types.InlineKeyboardButton('«      ', callback_data= 'folders_list')
    keyboard_markup.row(back_btn)
    
    get_samples_name = ""
    for  x in range(len(b_get_user_folders_list_with_keys (curent_user_id)[curent_folder_name])):
        get_samples_name+= str(list(b_get_user_folders_list_with_keys(curent_user_id)[curent_folder_name])[x]) + "\n"
        print(get_samples_name)
    await message.edit_text("Вы работаете с папкой : " + str(folder_name) + "\n" + "\n" + 
                        "Список аудио сэмлов : \n" + get_samples_name
                        + "\n"+ "Ваши действия - ", reply_markup=keyboard_markup)

async def remove_audio_samples(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for  x in range(len(b_get_user_folders_list_with_keys (curent_user_id)[curent_folder_name])):
        keyboard.add(str(list(b_get_user_folders_list_with_keys(curent_user_id)[curent_folder_name])[x]))
    await message.answer("Выберите блюдо которую хотите удалить:", reply_markup=keyboard)
    await Remove_Simples.remove_audio_samples_step_2.set()
    
    
@dp.message_handler(state= Remove_Simples.remove_audio_samples_step_2, content_types=types.ContentTypes.TEXT)
async def f_remove_audio_samples_step_2(msg: types.Message, state: FSMContext):
    await state.update_data(chosen_food=msg.text)
    user_data = await state.get_data()
    b_delete_audio_sample(curent_folder_name, user_data['chosen_food'])
    await msg.answer(f"Сэмпл {user_data['chosen_food']} успешно удален.", reply_markup=types.ReplyKeyboardRemove())
    await state.finish()
    await f_folder_list(msg, 'start') 
    
async def upload_audio_samples(message):
    keyboard_markup = types.InlineKeyboardMarkup()
    back_btn = types.InlineKeyboardButton('«      ', callback_data= curent_folder_name)
    keyboard_markup.row(back_btn)
    await message.edit_text("Вы работаете с папкой : " + str(curent_folder_name) + "\nЖду от тебя аудио сэмплы", reply_markup=keyboard_markup)
    await Upload_Simples.upload_audio_samples_step_2.set()


@dp.message_handler(state= Upload_Simples.upload_audio_samples_step_2, content_types=types.ContentTypes.AUDIO | types.ContentTypes.DOCUMENT)
async def f_upload_audio_samples_step_2(message: types.Message, state: FSMContext):
    await state.update_data(audio_sample_message=message)
    
    keyboard_markup = types.InlineKeyboardMarkup()
    back_btn = types.InlineKeyboardButton('«      ', callback_data= 'folders_list')
    keyboard_markup.row(back_btn)
    await bot.send_message(message.from_user.id, "Введите название вашей аудио записи : ", reply_markup=keyboard_markup)
    
    await Upload_Simples.upload_audio_samples_step_3.set()
    
    
    
@dp.message_handler(state= Upload_Simples.upload_audio_samples_step_3, content_types=types.ContentTypes.TEXT)
async def f_upload_audio_samples_step_3(msg: types.Message, state: FSMContext):
    await state.update_data(audio_sample_name=msg.text)
    user_data = await state.get_data()
    document_id = user_data["audio_sample_message"].document.file_id
    for  x in range(len(b_get_user_folders_list_with_keys (curent_user_id)[curent_folder_name])):
        if str(user_data["audio_sample_name"]).lower() == str(list(b_get_user_folders_list_with_keys(curent_user_id)[curent_folder_name])[x]).lower():
            await msg.reply("Данная запись уже существует, введите другое имя : ")
            return
    name_file = user_data["audio_sample_message"].document.file_name
    curent_file_extensions =  os.path.splitext(name_file)[1]
    #random_chrt = password_generate.easy_pass(30)
    if curent_file_extensions in ('.wav', '.mp3', '.wma'):
        await bot.send_message(msg.from_user.id,  'Идет загрузка файла....\nПодождите...')
        #await bot.download_file_by_id(file_id=document_id, destination= 'audio_samples/' + str(curent_user_id) + '/' + random_chrt + curent_file_extensions)
        await msg.reply(f'Файл с названием {user_data["audio_sample_name"]} успешно сохранён')
        b_reg_new_audio_sample(curent_folder_name, user_data["audio_sample_name"], document_id)
        await state.finish()
        await f_folder_list(msg, 'start') 
    else:
        await msg.reply('Мы такой формат не принемаем, пришлите в другом формате\nИзвините за неудобства!')
        return

@dp.errors_handler(exception=BotBlocked)
async def error_bot_blocked(update: types.Update, exception: BotBlocked):
    # Update: объект события от Telegram. Exception: объект исключения
    # Здесь можно как-то обработать блокировку, например, удалить пользователя из БД
    print(f"Меня заблокировал пользователь!\nСообщение: {update}\nОшибка: {exception}")

    # Такой хэндлер должен всегда возвращать True,
    # если дальнейшая обработка не требуется.
    return True

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
