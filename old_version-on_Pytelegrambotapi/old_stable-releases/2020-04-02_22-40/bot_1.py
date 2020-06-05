import telebot
from telebot import types
import sqlite3
import password_generate
#global call
BOT_TOKEN = "977180694:AAEXJHs1k3KT5Lmw2oz20QaS5ZGhS8bGY_8"
pwd_length = 10
a=True
bot = telebot.TeleBot(BOT_TOKEN)

def process(message):
    keyboard = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Простой', callback_data='pwd1')
    btn2 = types.InlineKeyboardButton('Средний', callback_data='pwd2')
    btn3 = types.InlineKeyboardButton('Сложный', callback_data='pwd3')
    keyboard.add(btn1, btn2, btn3)
    bot.send_message(message.chat.id, 'Выберите сложность пароля:', reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == "start":
        keyboard = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton('Простой', callback_data='pwd1')
        btn2 = types.InlineKeyboardButton('Средний', callback_data='pwd2')
        btn3 = types.InlineKeyboardButton('Сложный', callback_data='pwd3')
        keyboard.add(btn1, btn2, btn3)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="️Выбери сложность пароля️", reply_markup=keyboard)
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
        bot.answer_callback_query(callback_query_id=call.id, show_alert=False,
                text="🎛️ Настройки : Выбран русский язык 🇷🇺")
        con = sqlite3.connect('myTable.db', check_same_thread=False)
        cur = con.cursor()
        cur.execute("INSERT INTO users VALUES (?, ?)", (users_login, 'Ru'))
        con.commit()
        con.close()
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Ок.Для продолжения нажмтье /start",
				reply_markup=None)
        #bot.register_next_step_handler(message, process)
    if call.data =="set_lang-en":
        bot.answer_callback_query(callback_query_id=call.id, show_alert=False,
                text="🎛️ Настройки : Выбран: English 🇺🇸")
        con = sqlite3.connect('myTable.db', check_same_thread=False)
        cur = con.cursor()
        cur.execute("INSERT INTO users VALUES (?, ?)", (users_login, 'En'))
        con.commit()
        con.close()
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Ок.Для продолжения нажмтье /start",
				reply_markup=None)
#bot.register_next_step_handler(message, process) 
@bot.message_handler(commands=['start'])
#bot.register_next_step_handler(message, process)
def send_welcome(message):
    global users_login
    users_login = message.from_user.id
    con = sqlite3.connect('myTable.db', check_same_thread=False)
    cur = con.cursor()
    try:
        sql_UserName= "SELECT * FROM users Where User_id=?"
        cur.execute(sql_UserName, [(users_login)])
        get_sql_UserName = cur.fetchall()
        if str(get_sql_UserName[0][0]) == str(message.from_user.id):
        	#print(message)
        	print('Ваш id есть в БД! Идем дальще...')
        	process(message)
        #	bot.register_next_step_handler(message, process)
    except IndexError:
                print('Ваш id отсутствует в БД!')
                keyboard = types.InlineKeyboardMarkup()
                callback_button_1 = types.InlineKeyboardButton(text="English 🇺🇸", callback_data="set_lang-en")
                callback_button_2 = types.InlineKeyboardButton(text="Russian 🇷🇺", callback_data="set_lang-ru")
                keyboard.add(callback_button_1,callback_button_2)
                bot.send_message(message.chat.id, 'Please select your language:', reply_markup=keyboard)
    
    #print(get_sql_UserName[0][0])
    #entities= ('2','4')
    #con = sqlite3.connect('myTable.db', check_same_thread=False)
    
    #cur.execute("INSERT INTO users VALUES (?, ?)", entities)
  #  con.commit()
    #con.close()


if __name__ == '__main__':
    bot.skip_pending = True
    bot.polling(none_stop=True, interval=2)
