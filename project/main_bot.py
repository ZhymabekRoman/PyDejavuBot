""" PyDejavuBot
Бот-помощник для решения музыкальных викторин. Бот написан на aiogram.

/start - открыть глааное меню
"""


##Region ### START imports section ###
#from threading import Thread  #for using thread
import config
#import time
import logging
#import asyncio
from aiogram.utils.exceptions import BotBlocked
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext # for using FSM
import sqlite3 # for working with DB
import os.path # need for extract extions of file
import json #нужен для работы с json-кодированными данными
#import password_generate # фнукции для генерации паролей
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


def b_get_text_in_lang(data):
	dict_miltilang = {
	    '1' : {'Ru' : '🎛️ Настройки : Выбран русский язык 🇷🇺',
	             'En' : "🎛️ Setings : Selected English 🇺🇸 language!"},
	    '2' : {'Ru' : 'Настройки ⚙️',
	             'En' : 'Settings ⚙️'}
	}
	return dict_miltilang[data][lang_type]

def cache_update_curent_folder_name(folder_name):
    global curent_folder_name
    curent_folder_name = folder_name

def merge_two_dicts(x, y):
    """Given two dictionaries, merge them into a new dict as a shallow copy."""
    z = x.copy()
    z.update(y)
    return z
    
##Region ### START backends section ###
def b_get_user_folders_list_with_keys(user_id):
    return json.loads(b_get_user_data(user_id)[2]) #расшифровывем json кодированные данные

def b_get_user_folders_count(user_id):
    return  len(b_get_user_folders_list_with_keys(user_id))

def b_get_user_data(user_id):
    con = sqlite3.connect('myTable.db', check_same_thread=False)
    cur = con.cursor()
    cur.execute("SELECT * FROM users Where user_id= :0", {'0': user_id})
    con = sqlite3.connect('myTable.db', check_same_thread=False)
    out = cur.fetchone()
    con.close()
    print(out)
    return out
        
def b_delete_folder(user_id, folder_name):
    b_delete_all_audio_sample_from_folder(user_id, curent_folder_name)
    
    get_projects = b_get_user_folders_list_with_keys(user_id)
    del get_projects[folder_name]
    data_to_add = json.dumps(get_projects)
    con = sqlite3.connect('myTable.db', check_same_thread=False)
    cur = con.cursor()
    cur.execute("UPDATE users SET projects =  :0 WHERE User_id = :1", {'0': data_to_add, '1': user_id})
    con.commit()
    con.close()

def b_create_empety_db_data(user_id):
    if b_get_user_data(user_id) is None:
        con = sqlite3.connect('myTable.db', check_same_thread=False)
        cur = con.cursor()
        cur.execute("INSERT INTO users VALUES (:0, :1, :2)", {'0': user_id, '1': '', '2': '{}'})
        con.commit()
        con.close()

def b_set_lang(user_id, lang_name):
        con = sqlite3.connect('myTable.db', check_same_thread=False)
        cur = con.cursor()
        cur.execute("UPDATE users SET Lang = :0 WHERE User_id = :1", {'0': lang_name, '1': user_id})
        con.commit()
        con.close()

def b_reg_new_folder(current_user_id, folder_name):
    new_data = {}
    new_data[folder_name] = {}
    get_projects = b_get_user_folders_list_with_keys(current_user_id)
    data_to_add = json.dumps(merge_two_dicts(get_projects, new_data))
    con = sqlite3.connect('myTable.db', check_same_thread=False)
    cur = con.cursor()
    cur.execute("UPDATE users SET projects =  :0 WHERE User_id = :1", {'0': data_to_add, '1': current_user_id})
    con.commit()
    con.close()
    
def b_reg_new_audio_sample(current_user_id, folder_name, sample_name, file_id):
    abc = b_get_user_folders_list_with_keys(current_user_id) # {'Djxhhx' : {'lllpl' : 'fuuff'}, 'Jdjdjd' : {}}
    new_data = {}
    new_data[sample_name] = file_id # присваевает новые значения из аргументов
    data_to_merge = merge_two_dicts(abc[folder_name], new_data)
    abc[folder_name] = data_to_merge
    data_to_add = json.dumps(abc)
    con = sqlite3.connect('myTable.db', check_same_thread=False)
    cur = con.cursor()
    cur.execute("UPDATE users SET projects =  :0  WHERE User_id = :1", {'0': data_to_add, '1': current_user_id})
    con.commit()
    con.close()
    
def b_delete_all_audio_sample_from_folder(current_user_id, folder_name):
    abc = b_get_user_folders_list_with_keys(current_user_id)# {'Djxhhx' : {'lllpl' : 'fuuff'}, 'Jdjdjd' : {}}
    new_data = {}
    abc[folder_name] = new_data
    data_to_add = json.dumps(abc)
    con = sqlite3.connect('myTable.db', check_same_thread=False)
    cur = con.cursor()
    cur.execute("UPDATE users SET projects =  :0 WHERE User_id = :1", {'0': data_to_add, '1': current_user_id})
    con.commit()
    con.close()
    
def b_delete_audio_sample(current_user_id, folder_name, sample_name):
    abc = b_get_user_folders_list_with_keys(current_user_id)# {'Djxhhx' : {'lllpl' : 'fuuff'}, 'Jdjdjd' : {}}
    new_data = abc[folder_name]
    del new_data[sample_name]
    abc[folder_name] = new_data
    data_to_add = json.dumps(abc)
    con = sqlite3.connect('myTable.db', check_same_thread=False)
    cur = con.cursor()
    cur.execute("UPDATE users SET projects =  :0 WHERE User_id = :1", {'0': data_to_add, '1': current_user_id})
    con.commit()
    con.close()
##EndRegion ### END backends section ###

@dp.message_handler(commands=['start'], state='*')
async def send_welcome(message: types.Message):
    b_create_empety_db_data(message.chat.id)
    if b_get_user_data(message.chat.id)[1] == '':
        await f_set_lang(message, 'start')
    else:
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
    answer_data = query.data
    if answer_data == 'welcome_message':
        await query.answer()
        await f_welcome_message(query.message, 'edit')
    if answer_data == 'set_lang-ru':
        await query.answer(' 🎛️ Настройки : Выбран русский язык 🇷🇺')
        b_set_lang(query.message.chat.id,'Ru')
        await f_welcome_message(query.message, 'edit')
    if answer_data == 'set_lang-en':
        await query.answer('Бот в процесе разработки. В данное время поддерживается только русскии язык')
#        await query.answer('🎛️ Setings : Selected English 🇺🇸 language!')
#        b_set_lang(query.message.chat.id,'En')
#        await f_welcome_message(query.message, 'edit')
    if answer_data == 'set_lang-kz':
        await query.answer('Бот в процесе разработки. В данное время поддерживается только русскии язык')
#        await query.answer('🎛️ Setings : Selected Kazakh 🇰🇿 language!')
#        b_set_lang(query.message.chat.id,'Kz')
#        await f_welcome_message(query.message, 'edit')
    if answer_data == 'about_bot':
        await query.answer()
        keyboard_markup = types.InlineKeyboardMarkup()
        back_btn = types.InlineKeyboardButton('«      ', callback_data= 'welcome_message')
        keyboard_markup.row(back_btn)
        await query.message.edit_text("Разработчик ботка : @Zhymabek_Roman\nТех.поддержка : @Zhymabek_Roman", reply_markup=keyboard_markup)
    if answer_data == 'bot_settings':
        await query.answer()
        keyboard_markup = types.InlineKeyboardMarkup()
        back_btn = types.InlineKeyboardButton('«      ', callback_data= 'welcome_message')
        lang_btn = types.InlineKeyboardButton(f'Язык : {b_get_user_data(query.message.chat.id)[1]}', callback_data= 'edit_lang')
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
        if int(b_get_user_folders_count(query.message.chat.id)) < 7:
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
        if len(b_get_user_folders_list_with_keys(query.message.chat.id)[curent_folder_name]) == 0:
            await query.answer('У вас нету аудио сэмлов', True)
            return
        await query.answer()
        await f_remove_audio_samples_step_1(query.message)
    if answer_data == 'process_to_delete_folder':
        await f_delete_folder_step_2(query.message)
    for w in b_get_user_folders_list_with_keys(query.message.chat.id):
        if answer_data == w:
            await state.finish()
            await query.answer()
            await manage_folder(query.message, str(w))

async def f_delete_folder_step_1(message):
    keyboard_markup = types.InlineKeyboardMarkup()
    delete_btn = types.InlineKeyboardButton('Да!', callback_data= 'process_to_delete_folder')
    keyboard_markup.row(delete_btn)
    back_btn = types.InlineKeyboardButton('«      ', callback_data= 'folders_list')
    keyboard_markup.row(back_btn)
    await message.edit_text(f"Вы действительно хотите удалить папку {curent_folder_name}?\nЭТО ДЕЙСТВИЕ НЕЛЬЗЯ ОТМЕНИТЬ!", reply_markup=keyboard_markup)

async def f_delete_folder_step_2(message):
    b_delete_folder(message.chat.id, curent_folder_name)
    await message.edit_text(f"Папка {curent_folder_name} удалена!")
    await f_folder_list(message, 'start')

@dp.message_handler(state = Create_Folders.create_new_folder_step_1, content_types=types.ContentTypes.TEXT)
async def f_create_new_folder_step_1(message: types.Message):
    keyboard_markup = types.InlineKeyboardMarkup()
    back_btn = types.InlineKeyboardButton('«      ', callback_data= 'folders_list')
    keyboard_markup.row(back_btn)
    await message.edit_text("Введите название вашей папки : ", reply_markup=keyboard_markup)   
    await Create_Folders.create_new_folder_step_2.set()

@dp.message_handler(state = Create_Folders.create_new_folder_step_2, content_types=types.ContentTypes.TEXT)
async def f_create_new_folder_step_2(message: types.Message, state: FSMContext):
    if len(message.text) <=  10: #если длина папки будет меньше 10 символов, тогда ..... 
        for x in b_get_user_folders_list_with_keys(message.chat.id):
            if x.lower() == message.text.lower():
                await message.reply('Данная папка уже существует! Введите другое имя')
                return
        b_reg_new_folder(message.chat.id, message.text)
        await message.reply(f"Папка {message.text} создана!")
        await f_folder_list(message, 'start') 
        await state.finish()
    else:
        await message.reply('Название папки превышает 10 символов')
        return
        
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
    keyboard_markup = types.InlineKeyboardMarkup()
    create_new_folder_btn = types.InlineKeyboardButton('Создать новую папку 🗂', callback_data= 'create_new_folder')
    keyboard_markup.row(create_new_folder_btn)
    
    for folder_name in b_get_user_folders_list_with_keys(message.chat.id):
        get_sample_count = len(b_get_user_folders_list_with_keys(message.chat.id)[folder_name])
        folder_btn = types.InlineKeyboardButton(f"{folder_name} ({get_sample_count})", callback_data= folder_name)
        keyboard_markup.row(folder_btn)
 
    back_btn = types.InlineKeyboardButton('«      ', callback_data= 'welcome_message')
    keyboard_markup.row(back_btn)
    if type_start == 'start':
        await message.answer("Менеджер папок\n\nОбщее количество папок: {0}".format(b_get_user_folders_count(message.chat.id)), reply_markup=keyboard_markup)
    elif type_start == 'edit':
        await message.edit_text("Менеджер папок\n\nОбщее количество папок: {0}".format(b_get_user_folders_count(message.chat.id)), reply_markup=keyboard_markup)
    
        
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
    for i, b in enumerate(b_get_user_folders_list_with_keys(message.chat.id)[curent_folder_name], 1):
        get_samples_name += str(f"{i}) {b}\n")
    
    await message.edit_text("Вы работаете с папкой : " + str(folder_name) + "\n" + "\n" + 
                        "Список аудио сэмлов : \n" + get_samples_name
                        + "\n"+ "Ваши действия - ", reply_markup=keyboard_markup)

@dp.message_handler(state= Remove_Simples.remove_audio_samples_step_1)
async def f_remove_audio_samples_step_1(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    
    keyboard.add("<<< Отмена >>>")
    for i in b_get_user_folders_list_with_keys(message.chat.id)[curent_folder_name]:
        keyboard.add(str(i))
    keyboard.add("<<< Отмена >>>")
    
    await message.edit_text(f"Количество аудио сэмлов в этой папке : {len(b_get_user_folders_list_with_keys(message.chat.id)[curent_folder_name])}")
    await message.answer("Выберите аудио сэмпл который хотите удалить:", reply_markup=keyboard)
    await Remove_Simples.remove_audio_samples_step_2.set()
    
@dp.message_handler(state= Remove_Simples.remove_audio_samples_step_2, content_types=types.ContentTypes.TEXT)
async def f_remove_audio_samples_step_2(message: types.Message, state: FSMContext):
    await state.update_data(chosen_sample=message.text)
    user_data = await state.get_data()
    if user_data['chosen_sample'] == "<<< Отмена >>>":
        logging.info("<<< Отмена >>>")
        await message.reply("Вы отменили операцию", reply_markup=types.ReplyKeyboardRemove())
        await state.finish()
        await f_folder_list(message, 'start') 
        return 
    try:
        b_delete_audio_sample(message.chat.id, curent_folder_name, user_data['chosen_sample'])
    except KeyError:
        await message.reply("Такого аудио сэмпла нету. Выходим ...", reply_markup=types.ReplyKeyboardRemove())
        await state.finish()
        await f_folder_list(message, 'start') 
        return 
    await message.reply(f"Сэмпл {user_data['chosen_sample']} успешно удален.", reply_markup=types.ReplyKeyboardRemove())
    await state.finish()
    await f_folder_list(message, 'start') 

@dp.message_handler(state = Upload_Simples.upload_audio_samples_step_1)
async def f_upload_audio_samples_step_1(message):
    keyboard_markup = types.InlineKeyboardMarkup()
    back_btn = types.InlineKeyboardButton('«      ', callback_data= curent_folder_name)
    keyboard_markup.row(back_btn)
    await message.edit_text(f"Вы работаете с папкой : {curent_folder_name}\nЖду от тебя аудио сэмплы", reply_markup=keyboard_markup)
    await Upload_Simples.upload_audio_samples_step_2.set()


@dp.message_handler(state = Upload_Simples.upload_audio_samples_step_2, content_types=types.ContentTypes.AUDIO | types.ContentTypes.DOCUMENT)
async def f_upload_audio_samples_step_2(message: types.Message, state: FSMContext):
    await state.update_data(audio_sample_message=message)
    user_data = await state.get_data()
    
    name_file = user_data["audio_sample_message"].document.file_name
    curent_file_extensions =  os.path.splitext(name_file)[1]
    
    if curent_file_extensions in ('.wav', '.mp3', '.wma', '.ogg'):
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
    document_id = user_data["audio_sample_message"].document.file_id
    if len(str(user_data["audio_sample_name"])) >= 50:
        await message.reply('Название файла превышает 50 символов')
        return
        
    for  x in b_get_user_folders_list_with_keys (message.chat.id)[curent_folder_name]:
        if str(user_data["audio_sample_name"]).lower() == str(x).lower():
            await message.reply("Данная запись уже существует, введите другое имя : ")
            return
            
    await bot.send_message(message.from_user.id,  'Идет загрузка файла....\nПодождите...')
    #await bot.download_file_by_id(file_id=document_id, destination= 'audio_samples/' + str(curent_user_id) + '/' + random_chrt + curent_file_extensions)
    #await asyncio.sleep()
    await message.reply(f'Файл с названием {user_data["audio_sample_name"]} успешно сохранён')
    b_reg_new_audio_sample(message.chat.id, curent_folder_name, user_data["audio_sample_name"], document_id)
    await state.finish()
    await f_folder_list(message, 'start') 

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
