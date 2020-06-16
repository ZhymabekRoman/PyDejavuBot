import telebot
import sqlite3
import time
from telebot import types
import password_generate
import json
'''
PyDejavuBot
!WIP - Рассылка!
'''
        
def listener(messages):
    for m in messages:
        if m.content_type == 'text':
            print(str(m.chat.first_name) + " [" + str(m.chat.id) + "]: " + m.text)
            
BOT_TOKEN = "977180694:AAEXJHs1k3KT5Lmw2oz20QaS5ZGhS8bGY_8"
bot = telebot.TeleBot(BOT_TOKEN)
bot.set_update_listener(listener)

pwd_length = 10

def get_text_in_lang(data, lang_type):
	dict_miltilang = {
	    'fruit': 'mango',
	    '1' : {'Ru' : '🎛️ Настройки : Выбран русский язык 🇷🇺','En' : "🎛️ Setings : Selected English 🇺🇸 language!"},
	    '2' : {'Ru' : 'Настройки ⚙️','En' : 'Settings ⚙️'}
	}
	return dict_miltilang[data][lang_type]

def set_lang(type):
    con = sqlite3.connect('myTable.db', check_same_thread=False)
    cur = con.cursor()
    all_data = cur.execute("SELECT * FROM users")
    try:
        if str(get_users(users_login)[0]) == str(users_login):
            cur.execute("UPDATE users SET Lang =  ? WHERE User_id = ?", (type,users_login))
            con.commit()
            con.close()
    except IndexError:
        cur.execute("INSERT INTO users VALUES (?, ?)", (users_login, type))
        con.commit()
        con.close()

def get_current_user_lang():
	return get_users(users_login)[1]

def get_users(rdp_data):
    if rdp_data == 'all':
        con = sqlite3.connect('myTable.db', check_same_thread=False)
        cur = con.cursor()
        sql_UserName1= "SELECT * FROM users"
        cur.execute(sql_UserName1)
        get_sql_UserName1 = cur.fetchall()
        return get_sql_UserName1
        #print(get_sql_UserName1)
    else:
        con = sqlite3.connect('myTable.db', check_same_thread=False)
        cur = con.cursor()
        sql_UserName= "SELECT * FROM users Where User_id= ?"
        cur.execute(sql_UserName, [(str(rdp_data))])
        get_sql_UserName = cur.fetchall()
        return get_sql_UserName[0]
    
def wellcome_msg(message,type_start):
    #bulk_msg()
    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Простой', callback_data='pwd1')
    btn2 = types.InlineKeyboardButton('Средний', callback_data='pwd2')
    btn3 = types.InlineKeyboardButton('Сложный', callback_data='pwd3')
    btn4 = types.InlineKeyboardButton('О боте 🤖', callback_data='about_bot')
    btn5 = types.InlineKeyboardButton(get_text_in_lang('2',get_current_user_lang()), callback_data='edit_settings')
    keyboard.add(btn1, btn2, btn3)
    keyboard.add(btn4, btn5)
    if type_start == 'a':
        bot.send_message(message.chat.id, 'Выберите сложность пароля:', reply_markup=keyboard)
    elif type_start == 'c':
    	bot.reply_to(message, 'Выберите сложность пароля:', reply_markup=keyboard)
    else:
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="️Выбери сложность пароля️", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == "start":
        wellcome_msg(call.message,'b')
    if call.data == "edit_settings":
        keyboard = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton('Язык : ' + get_users(users_login)[1], callback_data='edit_lang')
        btn2 = types.InlineKeyboardButton('«      ', callback_data='start')
        keyboard.add(btn2,btn1)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Выберите параметр который вы хотите изменить:", reply_markup=keyboard)
    if call.data == "about_bot":
        keyboard = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton('«      ', callback_data='start')
        keyboard.add(btn)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Разработка ботка : @ZhymabekRoman\nТех.поддержка : @ZhymabekRoman", reply_markup=keyboard)
    if call.data == "edit_lang":
        keyboard = types.InlineKeyboardMarkup()
        callback_button_1 = types.InlineKeyboardButton(text="English 🇺🇸", callback_data="set_lang-en")
        callback_button_2 = types.InlineKeyboardButton(text="Russian 🇷🇺", callback_data="set_lang-ru")
        keyboard.add(callback_button_1,callback_button_2)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Please select your language:", reply_markup=keyboard)
    if call.data == "pwd1":
        keyboard = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton('Перегенирировать', callback_data='pwd1')
        btn2 = types.InlineKeyboardButton('Вернутся в начало', callback_data='start')
        keyboard.add(btn1)
        keyboard.add(btn2)
        pwd = password_generate.easy_pass(pwd_length)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Твой пароль - `{0}`".format(pwd), reply_markup=keyboard, parse_mode='Markdown')
    if call.data == "pwd2":
        keyboard = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton('Перегенирировать', callback_data='pwd2')
        btn2 = types.InlineKeyboardButton('Вернутся в начало', callback_data='start')
        keyboard.add(btn1)
        keyboard.add(btn2)
        pwd = password_generate.medium_pass(pwd_length)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Твой пароль - `{0}`".format(pwd), reply_markup=keyboard, parse_mode='Markdown')
    if call.data == "pwd3":
        keyboard = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton('Перегенирировать', callback_data='pwd3')
        btn2 = types.InlineKeyboardButton('Вернутся в начало', callback_data='start')
        keyboard.add(btn1)
        keyboard.add(btn2)
        pwd = password_generate.hard_pass(pwd_length)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Твой пароль - `{0}`".format(pwd), reply_markup=keyboard, parse_mode='Markdown')
    if call.data =="set_lang-ru":
        bot.delete_message(call.message.chat.id,call.message.message_id)
        bot.answer_callback_query(callback_query_id=call.id, show_alert=False,
                text=get_text_in_lang('1','Ru'))
        set_lang('Ru')
        wellcome_msg(call.message,'a')
    if call.data =="set_lang-en":
        bot.delete_message(call.message.chat.id,call.message.message_id)
        bot.answer_callback_query(callback_query_id=call.id, show_alert=False,
                text=get_text_in_lang('1','En'))
        set_lang('En')
        wellcome_msg(call.message,'a')
        
@bot.message_handler(commands=['start'])
def send_welcome(message):
    global users_login
    users_login = message.from_user.id
    try:
        if str(get_users(users_login)[0]) == str(users_login):
        	wellcome_msg(message,'c')
    except IndexError:
                keyboard = types.InlineKeyboardMarkup()
                callback_button_1 = types.InlineKeyboardButton(text="English 🇺🇸", callback_data="set_lang-en")
                callback_button_2 = types.InlineKeyboardButton(text="Russian 🇷🇺", callback_data="set_lang-ru")
                keyboard.add(callback_button_1,callback_button_2)
                msg = bot.reply_to(message, 'Please select your language:', reply_markup=keyboard)
              
@bot.message_handler(commands=['bulk_msg'])
def bulk_msg(message):
    for i in range(len(get_users('all'))):
        print(get_users('all')[i][0])
        bot.send_message(get_users('all')[i][0], "Scanning complete, I know you now")
        time.sleep(2)

    #print(get_sql_UserName[0][0])
    #entities= ('2','4')
    #con = sqlite3.connect('myTable.db', check_same_thread=False)
    
    #cur.execute("INSERT INTO users VALUES (?, ?)", entities)
  #  con.commit()
    #con.close()


if __name__ == '__main__':
    bot.skip_pending = True
    bot.polling(none_stop=True, interval=0)
