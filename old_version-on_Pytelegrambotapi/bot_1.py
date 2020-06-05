import telebot #для работы бота
import sqlite3 #для работа с бд
import time#для  sleep
import os
from threading import Thread
import asyncio 
import requests
from telebot import types
import password_generate # фнукции для генерации паролей
import json #нужен для работы с json-кодированными данными
import urllib.request # request нужен для загрузки файлов от пользователя

global upload_audio_to_project
upload_audio_to_project = False

# def b_function_name - backend function
# def f_function_name - frontend function

#включаем дебагер 
#import pdb; pdb.set_trace()
'''
PyDejavuBot
!
'''
#        
#def listener(messages):
#    for m in messages:
#        if m.content_type == 'text':
#            print(str(m.chat.first_name) + " [" + str(m.chat.id) + "]: " + m.text)

#def debug(message,debug_to_console):
#    print(str(message.chat.first_name) + " [" + str(message.chat.id) + "]: " + str(debug_to_console))

#BOT_TOKEN = "977180694:AAEXJHs1k3KT5Lmw2oz20QaS5ZGhS8bGY_8"
#bot = telebot.TeleBot(BOT_TOKEN)
#bot.set_update_listener(listener)

#pwd_length = 10

'''
def chech_and_download():
    i = 1
    while os.path.exists('saved' + str(i)  + '.ogg'):
        i +=1
    return 'saved' + str(i)  + '.ogg'
'''
#def b_work_with_db(execute_data, execute_data1 = ''):
#    con = sqlite3.connect('myTable.db', check_same_thread=False)
#    cur = con.cursor()
#    cur.execute(execute_data)
#    if execute_data1 == 'fetchall()':
#        return cur.fetchall()
#    con.commit()
#    con.close()
#    
#def b_get_text_in_lang(data,lang_type):
#	dict_miltilang = {
#	    'fruit': 'mango',
#	    '1' : {'Ru' : '🎛️ Настройки : Выбран русский язык 🇷🇺','En' : "🎛️ Setings : Selected English 🇺🇸 language!"},
#	    '2' : {'Ru' : 'Настройки ⚙️','En' : 'Settings ⚙️'}
#	}
#	return dict_miltilang[data][lang_type]

#def set_lang(type):
#    try:
#        if str(get_users_data(current_user_id)[0]) == str(current_user_id): #если текущии юзер найден в db, тогда....
#            b_work_with_db("UPDATE users SET Lang = '{0}' WHERE User_id = '{1}'".format(type,current_user_id))
#    except IndexError: #если текущии юзер не будет найден в db, тогда....
#        b_work_with_db("INSERT INTO users VALUES ('{0}', '{1}', '{2}')".format(current_user_id, type, '{}'))
#        cache_update_curent_user_proj()

#def delete_project_db(message, type):
#    get_projects = get_curent_user_proj()
#    for proj_name, proj_id in get_projects.items():
#        if  proj_name== type:
#            print(proj_id)
#            b_work_with_db("DELETE FROM projects WHERE project_id = '{0}'".format(proj_id))
#    del get_projects[type]
#    data_to_add = json.dumps(get_projects)
#    b_work_with_db("UPDATE users SET projects =  '{0}' WHERE User_id = '{1}'".format(data_to_add, current_user_id))
#    cache_update_curent_user_proj()
#    bot.answer_callback_query(callback_query_id=haha, show_alert=False,text= "Папка " + str(type) + " удалена!")
#    project_list(message,'')

#def dejavu_mode():
#    return 'On'

#def set_new_project(type):
#    generate_random_chrt = password_generate.easy_pass(30)
#    xxx = {}
#    xxx[type] = generate_random_chrt
#    get_projects = get_curent_user_proj()
#    if get_projects == '':
#    	data_to_add = json.dumps(xxx)
#    else:
#        res = {**get_projects, **xxx}
#        data_to_add = json.dumps(res)
#    b_work_with_db("UPDATE users SET projects =  '{0}' WHERE User_id = '{1}'".format(data_to_add, current_user_id))
#    b_work_with_db("INSERT INTO projects VALUES ('{0}', '{1}')".format(generate_random_chrt ,'{}'))
#    cache_update_curent_user_proj()
#        
#def cache_update_curent_user_proj():
#    global gogen
#    gogen = get_curent_user_proj()
#def get_current_user_lang():
#	return get_users_data(current_user_id)[1]
#def get_curent_user_proj():
#    return json.loads(get_users_data(current_user_id)[2])
#def get_curent_user_proj_count():
#    return  len(get_curent_user_proj())
    
#def get_users_data(rdp_data):
#    if rdp_data == 'all':
#        get_sql = b_work_with_db("SELECT * FROM users", 'fetchall()')
#        return get_sql
#    else:
#        get_sql = b_work_with_db("SELECT * FROM users Where User_id= '{0}'".format(rdp_data), 'fetchall()')
#        return get_sql[0]

#def add_new_audio_sample(file_name,sample_name):
#    pass
                                 #bacend_region_ends#
#=============================================================#
#def wellcome_msg(message,type_start):
#    keyboard = types.InlineKeyboardMarkup()
#    btn1 = types.InlineKeyboardButton('Папки', callback_data='project_list')
#    btn2 = types.InlineKeyboardButton('Режим "Dejavu" ' + dejavu_mode(), callback_data='create_new_project')
#    btn4 = types.InlineKeyboardButton('О боте 🤖', callback_data='about_bot')
#    btn5 = types.InlineKeyboardButton(b_get_text_in_lang('2',get_current_user_lang()), callback_data='edit_settings')
#    keyboard.add(btn1)
#    keyboard.add(btn4, btn5)
#    keyboard.add(btn2)
#    if type_start == 'a':
#        bot.send_message(message.chat.id, 'Выберите сложность пароля:', reply_markup=keyboard)
#    elif type_start == 'c':
#    	bot.reply_to(message, 'Выберите сложность пароля:', reply_markup=keyboard)
#    else:
#        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="️Выбери сложность пароля️", reply_markup=keyboard)
        
#def project_list(message,type_start):
#        #debug(message,'Projects counts ' + str(get_curent_user_proj_count()))
#        keyboard = types.InlineKeyboardMarkup()
#        btn1 = types.InlineKeyboardButton('Создать новую папку 🗂 ', callback_data='create_new_project')
#        btn3 = types.InlineKeyboardButton('«                          ', callback_data='start')
#        keyboard.add(btn1)
#        for x in range(get_curent_user_proj_count()):
#            y  = types.InlineKeyboardButton(str(list(get_curent_user_proj())[x]), callback_data= str(list(get_curent_user_proj())[x]))
#            keyboard.add(y)
#        keyboard.add(btn3)
#        if type_start == 'a':
#            bot.send_message(message.chat.id, "Выберите папку : ", reply_markup=keyboard)
#        else:
#            bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Выберите папку : ", reply_markup=keyboard)
#     	
#def create_new_project(message, type_start):
#    if int(get_curent_user_proj_count()) <7:
#        keyboard = types.InlineKeyboardMarkup()
#        btn2 = types.InlineKeyboardButton('«      ', callback_data='project_list')
#        keyboard.add(btn2)
#        if type_start == 'a':
#            msg = bot.send_message(message.chat.id, "", reply_markup=keyboard)
#        else:
#            msg = bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Введите название вашей папки : ", reply_markup=keyboard)
#        bot.register_next_step_handler(msg, register_new_project)
#    else:
#        bot.answer_callback_query(callback_query_id=haha, show_alert=True,text= "Список папок превышает 7")
    
#def register_new_project(message):
#    #print(get_curent_user_proj())
#    try:
#        dif = len(message.text)
#    except:
#        print('except work')
#        create_new_project(message, 'a')
#        return
#    if int(dif) <= int(10): #если длина папки будет меньше 10 символов, тогда .....
#        for x in range(get_curent_user_proj_count()):
#             if  list(get_curent_user_proj())[x] == message.text:
#                 bot.answer_callback_query(callback_query_id=haha, show_alert=True,text= "Данная папка уже существует! Введите другое имя")
#                 print('xxxxxx')
#                 create_new_project(message,'a')
#                 return 
#        set_new_project(message.text)
#        bot.answer_callback_query(callback_query_id=haha, show_alert=False,text= "Папка " + str(message.text) + " создана!")
#        bot.delete_message(message.chat.id,message.message_id-1)
#        bot.delete_message(message.chat.id,message.message_id)
#        project_list(message,"a")
#    else: 
#        bot.reply_to(message, "Название папки превышает 10 символов!")
#        create_new_project(message,'a')

#def delete_project(message):
#    keyboard = types.InlineKeyboardMarkup()
#    btn1 = types.InlineKeyboardButton('Да!', callback_data='delete_project_conf')
#    btn2 = types.InlineKeyboardButton('«      ', callback_data='project_list')
#    keyboard.add(btn1)
#    keyboard.add(btn2)
#    msg = bot.edit_message_text(chat_id =message.chat.id, message_id = message.message_id,text =  'Вы действительно хотите удалить папку?\nЭТО ДЕЙСТВИЕ НЕЛЬЗЯ ОТМЕНИТЬ!' , reply_markup=keyboard)
    
#def manage_projects(message,proj_name):
    #global upload_audio_to_project
    #upload_audio_to_project = False
#    keyboard = types.InlineKeyboardMarkup()
#    btn0 = types.InlineKeyboardButton('Загрузить образцы аудио', callback_data='upload_audio_samples')
#    btn1 = types.InlineKeyboardButton('Удалить папкy 🗑', callback_data='delete_project')
#    btn2 = types.InlineKeyboardButton('«      ', callback_data='project_list')
#    keyboard.add(btn0)
#    keyboard.add(btn1)
#    keyboard.add(btn2)
#    msg = bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Проект : " + str(proj_name) + '\n\nВаше действия : ', reply_markup=keyboard)
#    global grom
#    grom =  str(proj_name)
    
def upload_audio_samples(message,proj_name):
    print('Go go go ' + proj_name)
    global upload_audio_to_project
    upload_audio_to_project = True
    keyboard = types.InlineKeyboardMarkup()
    btn0 = types.InlineKeyboardButton('Готово ✅', callback_data=str(proj_name))
    btn2 = types.InlineKeyboardButton('«      ', callback_data='project_list')
    keyboard.add(btn0)
    keyboard.add(btn2)
    msg = bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Проект : " + str(proj_name) + '\n\nСейчас вы можете мне отправлять аудио образцы викторины.\nПосле загрузки всех аудио нажмите кнопку "Готово" ', reply_markup=keyboard)
###############


################
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    global haha
    haha = call.id
#    if call.data == "start":
#        wellcome_msg(call.message,'b')
#    if call.data == "create_new_project":
#        create_new_project(call.message,'')
#    if call.data == "edit_settings":
#    	###
#        def timer(name):
#            count = 0
#            while count<13:
#                time.sleep(1)
#                count += 1            
#                print("Hi " + str(name) + " This program has now been running for " + str(count) + " minutes.")
#        background_thread = Thread(target=timer, args=(current_user_id,))
#        background_thread.start()
#    	#####
#        keyboard = types.InlineKeyboardMarkup()
#        btn1 = types.InlineKeyboardButton('Язык : ' + get_users_data(current_user_id)[1], callback_data='edit_lang')
#        btn2 = types.InlineKeyboardButton('«      ', callback_data='start')
#        keyboard.add(btn2,btn1)
#        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Выберите параметр который вы хотите изменить:", reply_markup=keyboard)
#    if call.data == "about_bot":
#        keyboard = types.InlineKeyboardMarkup()
#        btn = types.InlineKeyboardButton('«      ', callback_data='start')
#        keyboard.add(btn)
#        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Разработчик ботка : @ZhymabekRoman\nТех.поддержка : @ZhymabekRoman", reply_markup=keyboard)
#    if call.data == "edit_lang":
#        keyboard = types.InlineKeyboardMarkup()
#        callback_button_1 = types.InlineKeyboardButton(text="English 🇺🇸", callback_data="set_lang-en")
#        callback_button_2 = types.InlineKeyboardButton(text="Russian 🇷🇺", callback_data="set_lang-ru")
#        keyboard.add(callback_button_1,callback_button_2)
#        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Please select your language:", reply_markup=keyboard)
#    if call.data == "project_list":
#        global upload_audio_to_project
#        upload_audio_to_project = False
#        bot.clear_step_handler_by_chat_id(chat_id = call.message.chat.id)
#        project_list(call.message,"")
    if call.data == "upload_audio_samples":
        upload_audio_samples(call.message,grom)
#    if call.data == "delete_project":
#        delete_project(call.message)
#    if call.data == "delete_project_conf":
#        delete_project_db(call.message,grom)
#    if call.data == "pwd3":
#        keyboard = types.InlineKeyboardMarkup()
#        btn1 = types.InlineKeyboardButton('Перегенирировать', callback_data='pwd3')
#        btn2 = types.InlineKeyboardButton('Вернутся в начало', callback_data='start')
#        keyboard.add(btn1)
#        keyboard.add(btn2)
#        pwd = password_generate.hard_pass(pwd_length)
#        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Твой пароль - `{0}`".format(pwd), reply_markup=keyboard, parse_mode='Markdown')
#    if call.data =="set_lang-ru":
#        bot.delete_message(call.message.chat.id,call.message.message_id)
#        bot.answer_callback_query(callback_query_id=call.id, show_alert=False,
#                text=b_get_text_in_lang('1','Ru'))
#        set_lang('Ru')
#        wellcome_msg(call.message,'a')
#    if call.data =="set_lang-en":
#        bot.delete_message(call.message.chat.id,call.message.message_id)
#        bot.answer_callback_query(callback_query_id=call.id, show_alert=False,
#                text=b_get_text_in_lang('1','En'))
#        set_lang('En')
#        wellcome_msg(call.message,'a')
 #   for w in range(len(gogen)):
#        if call.data == list(gogen)[w]:
#            manage_projects(call.message,str(list(gogen)[w]))

#	########
#@bot.message_handler(commands=['start'])
#def send_welcome(message):
#    global upload_audio_to_project
#    upload_audio_to_project = False
#    global current_user_id
#    current_user_id = message.from_user.id
#    try:
#        cache_update_curent_user_proj()
#        if str(get_users_data(current_user_id)[0]) == str(current_user_id):
#        	wellcome_msg(message,'c')
#    except IndexError:
#                keyboard = types.InlineKeyboardMarkup()
#                callback_button_1 = types.InlineKeyboardButton(text="English 🇺🇸", callback_data="set_lang-en")
#                callback_button_2 = types.InlineKeyboardButton(text="Russian 🇷🇺", callback_data="set_lang-ru")
#                keyboard.add(callback_button_1,callback_button_2)
#                msg = bot.reply_to(message, 'Please select your language:', reply_markup=keyboard)
              
@bot.message_handler(commands=['bulk_msg'])
def bulk_msg(message):
    for i in range(len(get_users_data('all'))):
        bulk_text_data = message.text.split('/bulk_msg')[1]
        if bulk_text_data == '':
            print('Вы не ввели текст!')
        else:
            try:
                bot.send_message(get_users_data('all')[i][0], bulk_text_data, parse_mode="Markdown")
                print('Successful send message by user:' + get_users_data('all')[i][0])
                time.sleep(2)
            except telebot.apihelper.ApiException:
                print('Error send to user: ' + get_users_data('all')[i][0])

@bot.message_handler(content_types=["voice"])
def handle_docs_document(message):
    if upload_audio_to_project == True :
        debug(message, 'Voice getting....')
        voice_id = message.voice.file_id
        file_info = bot.get_file(voice_id)
        debug(message, 'Saving data : ' + '')
        print(message)
        urllib.request.urlretrieve(f'http://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}', 'tmp/' + password_generate.easy_pass(30) + '.ogg')
        debug(message, 'Done!')
    else:
         print('Gggghh')
    #bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAALO5V6-rPrbra_imDrMh-8ebvZpjFrCAAI6AAMCEG8zvQsImdZXsYMZBA', disable_notification = False, reply_to_message_id = message.message_id)

@bot.message_handler(content_types=["audio"])
def handle_docs_document(message):
    #if upload_audio_to_project == True :
        debug(message, 'Voice getting....')
        voice_id = message.audio.file_id
        file_info = bot.get_file(voice_id)
        debug(message, 'Saving data : ' + '')
        print(message)
        urllib.request.urlretrieve(f'http://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}', 'tmp/' + password_generate.easy_pass(30) + '.ogg')
        debug(message, 'Done!')
   # else:
     #    print('Gggghh')

@bot.message_handler(content_types=["document"])
def get_document(message):
    print('ffpjdjdp')
    print(message)
   
if __name__ == '__main__':
    bot.skip_pending = True
    bot.polling(none_stop=True, interval=0)
