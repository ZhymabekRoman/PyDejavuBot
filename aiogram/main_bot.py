### PyDejavuBot-

##Region ### START imports section ###
from threading import Thread  #for using thread
import time
import logging
import asyncio
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext # for using FSM
import sqlite3 # for working with DB
import os.path # need for extract extions of file
import json #нужен для работы с json-кодированными данными
import password_generate # фнукции для генерации паролей
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import urllib.request # for getting files from user
##EndRegion ### END imports section ###

API_TOKEN = '977180694:AAEXJHs1k3KT5Lmw2oz20QaS5ZGhS8bGY_8' # Initalialization API token for work with Telegram Bot

#ConfigureMemoryStorage
memory_storage = MemoryStorage()
# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=memory_storage)


class Create_Folders(StatesGroup):
    create_new_folder_step_2 = State()
class Upload_Simples(StatesGroup):
    upload_audio_samples_step_2 = State()
    upload_audio_samples_step_3 = State()

#initialize global vars for acces from anywhere
def cache_update_curent_user_proj():
    global curent_user_proj
    try:
        curent_user_proj = get_curent_user_proj()
    except TypeError:
    	curent_user_proj = ""
def cache_update_curent_folder_name(folder_name):
    global curent_folder_name
    curent_folder_name = folder_name
def cache_update_curent_user_id(msg):
    global curent_user_id
    curent_user_id = msg.chat.id
    print(curent_user_id)
def cache_update_query_global(query_data):
    global query_global
    query_global = query_data

def get_curent_user_proj_low_case():
    curent_user_proj = json.loads(b_get_curent_user_data(curent_user_id)[2])
    curent_user_proj_in_low_case = dict((k.lower(), v) for k, v in curent_user_proj .items())
    return curent_user_proj_in_low_case
def get_curent_user_proj():
    return json.loads(b_get_curent_user_data(curent_user_id)[2])
def get_curent_user_proj_count():
    return  len(get_curent_user_proj())
    
##Region ### START backends section ###
def b_get_curent_user_proj_data():
    get_curent_folders_id = get_curent_user_proj()[curent_folder_name] 
    con = sqlite3.connect('myTable.db', check_same_thread=False)
    cur = con.cursor()
    cur.execute("SELECT * FROM projects Where project_id = '{0}'".format(get_curent_folders_id))
    return cur.fetchall()[0]
    con.close()

def b_get_curent_user_data(curent_user_id_1):
        con = sqlite3.connect('myTable.db', check_same_thread=False)
        cur = con.cursor()
        cur.execute("SELECT * FROM users Where user_id= '{0}'".format(curent_user_id_1))
        return cur.fetchone()
        con.close()
        
def b_delete_project_db(message, folder_name):
    get_projects = get_curent_user_proj()
    for proj_name, proj_id in get_projects.items():
        if  proj_name== folder_name:
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
    cur.execute("UPDATE users SET projects =  '{0}' WHERE User_id = '{1}'".format(data_to_add, curent_user_id))
    con.commit()
    con.close()
    cache_update_curent_user_proj()

def b_set_lang(curent_user_id, lang_name):
    try:
        if str(b_get_curent_user_data(curent_user_id)[0]) == str(curent_user_id): #если текущии юзер найден в db, тогда....
            print(b_get_curent_user_data(curent_user_id)[0])
            con = sqlite3.connect('myTable.db', check_same_thread=False)
            cur = con.cursor()
            cur.execute("UPDATE users SET Lang = '{0}' WHERE User_id = '{1}'".format(lang_name,curent_user_id))
            con.commit()
            con.close()
    except TypeError: #если текущии юзер не будет найден в db, тoгда...')
            con = sqlite3.connect('myTable.db', check_same_thread=False)
            cur = con.cursor()
            cur.execute("INSERT INTO users VALUES ('{0}', '{1}', '{2}')".format(curent_user_id, lang_name, '{}'))
            con.commit()
            con.close()

def b_reg_new_folder(folder_name):
    generate_random_chrt = password_generate.easy_pass(30)
    new_data = {}
    new_data[folder_name] = generate_random_chrt
    get_projects = get_curent_user_proj()
    if get_projects == '{}':
        data_to_add = json.dumps(new_data)
    else:
        res = {**get_projects, **new_data}
        data_to_add = json.dumps(res)
    con = sqlite3.connect('myTable.db', check_same_thread=False)
    cur = con.cursor()
    cur.execute("UPDATE users SET projects =  '{0}' WHERE User_id = '{1}'".format(data_to_add, curent_user_id))
    cur.execute("INSERT INTO projects VALUES ('{0}', '{1}')".format(generate_random_chrt ,'{}'))
    con.commit()
    con.close()
    cache_update_curent_user_proj()
##EndRegion ### END backends section ###

@dp.message_handler(commands=['start'], state='*')
async def send_welcome(message: types.Message):
    cache_update_curent_user_id(message)

    print("First test - " + str(curent_user_id))
    print("Lenin test - " + str((b_get_curent_user_data(curent_user_id))))

    #str((cur.fetchone())[0]))
    #cache_update_curent_user_proj()
    try:
        if str((b_get_curent_user_data(curent_user_id))[0]) == str(curent_user_id): #если текущии юзер найден в db, тогда....
            print("1")
            cache_update_curent_user_proj()
            await f_welcome_message(message, 'send')
        else:
        	print("else except")
    except TypeError: #если текущии юзер не будет найден в db, тогда..
        print("2")
        await f_set_lang(message, 'start')

async def f_welcome_message(message: types.Message, type_start):
    keyboard_markup = types.InlineKeyboardMarkup()
    folder_list_btns = types.InlineKeyboardButton('Папки', callback_data= 'folders_list')
    about_btns = types.InlineKeyboardButton('О боте 🤖', callback_data= 'about_bot')
    setings_btns = types.InlineKeyboardButton('Настройки ⚙', callback_data= 'bot_settings')
    keyboard_markup.row(folder_list_btns)
    keyboard_markup.row(about_btns, setings_btns)
    if type_start == 'edit':
        await message.edit_text("Меню : ", reply_markup=keyboard_markup)
    elif type_start == 'send':
        await message.reply("Меню : ", reply_markup=keyboard_markup)

@dp.callback_query_handler(state='*')
async def callback_handler(query: types.CallbackQuery, state):
    cache_update_curent_user_id(query.message)
    cache_update_curent_user_proj()
    cache_update_query_global(query)
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
        lang_btn = types.InlineKeyboardButton('Язык : ' + b_get_curent_user_data(query.message.chat.id)[1], callback_data= 'edit_lang')
        keyboard_markup.row(back_btn,lang_btn)
        await query.message.edit_text("Настройки бота:", reply_markup=keyboard_markup)   
    if answer_data == 'edit_lang':
        await f_set_lang(query.message, 'edit')
    if answer_data == 'folders_list':
        await state.finish()
        await query.answer()
        await f_folder_list(query.message, 'edit')
    if answer_data == 'create_new_folder':
        if int(get_curent_user_proj_count()) < 7:
            await f_create_new_folder(query.message)
        else:
            await query.answer('Список папок превышает 7', True)
    if answer_data == 'folder_delete':
        keyboard_markup = types.InlineKeyboardMarkup()
        delete_btn = types.InlineKeyboardButton('Да!', callback_data= 'process_to_delete_folder')
        keyboard_markup.row(delete_btn)
        back_btn = types.InlineKeyboardButton('«      ', callback_data= 'folders_list')
        keyboard_markup.row(back_btn)
        await query.message.edit_text("Вы действительно хотите удалить папку?\nЭТО ДЕЙСТВИЕ НЕЛЬЗЯ ОТМЕНИТЬ!", reply_markup=keyboard_markup)
    if answer_data == 'upload_audio_samples':
        await upload_audio_samples(query.message)
    if answer_data == 'process_to_delete_folder':
        b_delete_project_db(query.message, curent_folder_name)
        await query.answer("Папка " + str(curent_folder_name) + " удалена!")
        await query.answer()
        await f_folder_list(query.message, 'edit')
    for w in range(len(curent_user_proj)):
        if answer_data == list(curent_user_proj)[w]:
            await state.finish()
            await query.answer()
            await manage_projects(query.message, str(list(curent_user_proj)[w]))
  
async def f_create_new_folder(message, type_start = 'send'):
        keyboard_markup = types.InlineKeyboardMarkup()
        back_btn = types.InlineKeyboardButton('«      ', callback_data= 'folders_list')
        keyboard_markup.row(back_btn)
        await message.edit_text("Введите название вашей папки : ", reply_markup=keyboard_markup)   
        await Create_Folders.create_new_folder_step_2.set()

@dp.message_handler(state= Create_Folders.create_new_folder_step_2, content_types=types.ContentTypes.TEXT)
async def f_create_new_folder_step_2(message: types.Message, state: FSMContext):
    if len(message.text) <=  int(10): #если длина папки будет меньше 10 символов, тогда ..... 
        for x in range(get_curent_user_proj_count()):
                 if  list(get_curent_user_proj_low_case())[x] == message.text.lower():
                     await query_global.answer('Данная папка уже существует! Введите другое имя', True)
                     return
        b_reg_new_folder(message.text)
        await query_global.answer("Папка " + str(message.text) + " создана!")
        await f_folder_list(message, 'start') 
        await state.finish()
    else:
        await query_global.answer('Название папки превышает 10 символов', True)
        await message.delete()
        #await state.finish()
        #await f_create_new_folder(message[-1])    #TODO
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

    for x in range(get_curent_user_proj_count()):
        text_data_btn = str(list(get_curent_user_proj())[x])
        y = types.InlineKeyboardButton(text_data_btn, callback_data= text_data_btn)
        keyboard_markup.row(y)
    back_btn = types.InlineKeyboardButton('«      ', callback_data= 'welcome_msg')
    keyboard_markup.row(back_btn)
    

    if type_start == 'start':
        await message.answer("Please select your language:", reply_markup=keyboard_markup)
    elif type_start == 'edit':
        await message.edit_text("Please select your language:", reply_markup=keyboard_markup)
    
        
async def manage_projects(message, folder_name):
    keyboard_markup = types.InlineKeyboardMarkup()
    delete_btn = types.InlineKeyboardButton('Удалить папкy 🗑', callback_data= 'folder_delete')
    keyboard_markup.row(delete_btn)
    upload_audio_samples_btn = types.InlineKeyboardButton('Загрузить аудио сэмплы', callback_data= 'upload_audio_samples')
    keyboard_markup.row(upload_audio_samples_btn)
    
    back_btn = types.InlineKeyboardButton('«      ', callback_data= 'folders_list')
    keyboard_markup.row(back_btn)
    
    cache_update_curent_folder_name(folder_name)
    vat = ""
    for  x in range(len(json.loads(b_get_curent_user_proj_data()[1]))):
        #print(str(list(json.loads(b_get_curent_user_proj_data()[1]))[x]))
        
        vat+= str(list(json.loads(b_get_curent_user_proj_data()[1]))[x]) + "\n"
        print(vat)
    await message.edit_text("Вы работаете с папкой : " + str(folder_name) + "\n" + 
                        "Список аудио сэмлов : \n" + vat
                        + "\n"+ "\nВаши действия - ", reply_markup=keyboard_markup)
    
async def upload_audio_samples(message):
        keyboard_markup = types.InlineKeyboardMarkup()
        back_btn = types.InlineKeyboardButton('«      ', callback_data= curent_folder_name)
        keyboard_markup.row(back_btn)
        await message.edit_text("Вы работаете с папкой : " + str(curent_folder_name) + "\nЖду от тебя аудио сэмплы", reply_markup=keyboard_markup)
        await Upload_Simples.upload_audio_samples_step_2.set()


@dp.message_handler(state= Upload_Simples.upload_audio_samples_step_2, content_types=types.ContentTypes.AUDIO | types.ContentTypes.DOCUMENT)
async def f_upload_audio_samples_step_2(message: types.Message, state: FSMContext):
        keyboard_markup = types.InlineKeyboardMarkup()
        back_btn = types.InlineKeyboardButton('«      ', callback_data= 'folders_list')
        keyboard_markup.row(back_btn)
        await bot.send_message(message.from_user.id, "Введите название вашей аудио записи : ", reply_markup=keyboard_markup)
    
    
    
#    if len(message.text) <=  int(10): #если длина папки будет меньше 10 символов, тогда ..... 
#        for x in range(get_curent_user_proj_count()):
#                 if  list(get_curent_user_proj_low_case())[x] == message.text.lower():
#                     await query_global.answer('Данная папка уже существует! Введите другое имя', True)
#                     return
#        b_reg_new_folder(message.text)
#        await query_global.answer("Папка " + str(message.text) + " создана!")
#        await f_folder_list(message, 'start') 
#        await state.finish()
#    else:
#        await query_global.answer('Название папки превышает 10 символов', True)
#        await message.delete()
#        #await state.finish()
#        #await f_create_new_folder(message[-1])    #TODO
#        return
        
        global first_data
        first_data = message.document.file_id
        global second_data
        second_data = message.document.file_name
        
        #await state.update_data(recive_data= message.document.file_id, recive_data_1 = message.document.file_name)
        await Upload_Simples.upload_audio_samples_step_3.set()
    
    
    
@dp.message_handler(state= Upload_Simples.upload_audio_samples_step_3, content_types=types.ContentTypes.TEXT)
async def f_upload_audio_samples_step_3(msg: types.Message, state: FSMContext):
    #document_id = msg.document.file_id
    #print(await state.get_data())
    #document_id = await state.get_data()['recive_data']
    document_id = first_data
    file_info = await bot.get_file(document_id)
    fi = file_info.file_path
    for x in range(len(json.loads(b_get_curent_user_proj_data()[1]))):
        if str(list(json.loads(b_get_curent_user_proj_data()[1]))[x]) == msg.text:
            await bot.send_message(msg.from_user.id, "Данная запись уже существует, введите другое имя : ")
            return
    name = msg.text
    #name_file = msg.document.file_name
    #name_file = await state.get_data()['recive_data_1']
    name_file = second_data
    curent_file_extensions =  os.path.splitext(name_file)[1]
    random_chrt = password_generate.easy_pass(30)
    get_curent_folders_id = get_curent_user_proj()[curent_folder_name] 
    if curent_file_extensions in ('.wav', '.mp3', '.wma'):
        await bot.send_message(msg.from_user.id,  'Идет загрузка файла....Подождите...')
        #urllib.request.urlretrieve(f'https://api.telegram.org/file/bot{API_TOKEN}/{fi}', 'audio_samples/' + random_chrt + curent_file_extensions)
        new_data = {}
        new_data[name] = random_chrt
        if b_get_curent_user_proj_data()[1] == '{}':
            data_to_add = json.dumps(new_data)
        else:
            curent_data = json.loads(b_get_curent_user_proj_data()[1])
            res = {**curent_data, **new_data}
            data_to_add = json.dumps(res)
             
        con = sqlite3.connect('myTable.db', check_same_thread=False)
        cur = con.cursor()
        cur.execute("UPDATE projects SET data = '{0}' WHERE project_id = '{1}'".format(data_to_add, get_curent_folders_id))
        con.commit()
        con.close()

        await bot.send_message(msg.from_user.id, 'Файл успешно сохранён')
        await f_folder_list(msg, 'start') 
        await state.finish()
    else:
        await bot.send_message(msg.from_user.id, 'Мы такой формат не принемаем, пришлите в другом формате\nИзвините за неудобства!')
        return
        
        
##Region ### START TODO section ###
#def timer(msg):         #TODO
#        count = 0
#        while True:
#            time.sleep(1)
#            count += 1
            #print("Hi " + name + " This program has now been running for " + str(count) + " seconds.")

   # background_thread = Thread(target=timer)
  
   # await background_thread.start()
   
# run discord_async_method() in the "background"
#asyncio.get_event_loop().create_task(timer(query.message))
  
#@dp.message_handler(content_types=types.ContentTypes.DOCUMENT)
#async def scan_message(msg: types.Message):
#    print("get document from user")
#    document_id = msg.document.file_id
#    file_info = await bot.get_file(document_id)
#    fi = file_info.file_path
#    name = msg.document.file_name
#    curent_file_extensions =  os.path.splitext(name)[1]
#    if curent_file_extensions in ('.wav', '.mp3', '.wma'):
#        print('Will be Ok!')
#        urllib.request.urlretrieve(f'https://api.telegram.org/file/bot{API_TOKEN}/{fi}', 'audio_samples/' + password_generate.easy_pass(30) + curent_file_extensions)
#        await bot.send_message(msg.from_user.id, 'Файл успешно сохранён')
#    else:
#        print('noooooo')
#        await bot.send_message(msg.from_user.id, 'Мы такой формат не принемаем, пришлите в другом формате\nИзвините за неудобства!')
#        #return     #TODO
#        
        
#####TODO 
#   try:
#        await bot.send_message(user_id, text, disable_notification=disable_notification)
#    except exceptions.BotBlocked:
#        log.error(f"Target [ID:{user_id}]: blocked by user")
#    except exceptions.ChatNotFound:
#        log.error(f"Target [ID:{user_id}]: invalid user ID")
#    except exceptions.RetryAfter as e:
#        log.error(f"Target [ID:{user_id}]: Flood limit is exceeded. Sleep {e.timeout} seconds.")
#        await asyncio.sleep(e.timeout)
#        return await send_message(user_id, text)  # Recursive call
#    except exceptions.UserDeactivated:
#        log.error(f"Target [ID:{user_id}]: user is deactivated")
#    except exceptions.TelegramAPIError:
#        log.exception(f"Target [ID:{user_id}]: failed")
#    else:
#        log.info(f"Target [ID:{user_id}]: success")
#        return True
#    return False
##EndRegion ### END TODO section ###

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)