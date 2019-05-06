from db_coin import db_session, CoinBase, User, UserQuery
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import API_file
import logging
import requests
import json
from sqlalchemy import exc
from sqlalchemy.exc import IntegrityError
from datetime import datetime, date, time
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from telegram import ReplyKeyboardMarkup
import asyncio
from sqlalchemy import or_, and_

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename='bot.log'
                    )

def get_bit(url):
    result = requests.get(url)
    if result.status_code == 200:
        return(result.json())
    else:
        print("Ошибка подключения")

def _up():
    data = get_bit("https://api.coinmarketcap.com/v1/ticker/?limit=10")
    for data_coin in data:
        
        name_coin = data_coin['name']
        price_coin = data_coin['price_usd']
        print(price_coin)
        print(name_coin)
        coin_in_db = db_session.query(CoinBase).filter(CoinBase.coin_name == name_coin).first()

        if not coin_in_db:
            coin = CoinBase(data_coin['name'].lower(), data_coin['price_usd'], datetime.utcnow())
            db_session.add(coin)
            db_session.commit()
            print("Добавлено значение - %s" % name_coin)

        else:
            print('обновляю значение')
            coin_in_db.price_usd = float(price_coin)
            db_session.add(coin_in_db)
            db_session.commit()

def db_update(bot, update, job_queue):
    _up()
    price_text = "База загружена"
    update.message.reply_text(price_text)

def coin_check(bot, update):
    user_chat_id = update['message']['chat']['id']
    base_chat_id = db_session.query(User)
    for user_chat_id1 in base_chat_id:
        user_chat_id_dict = user_chat_id1.__dict__['id_user_chat']
        coins = db_session.query(UserQuery).join(CoinBase).join(User).\
            filter(User.id_user_chat==user_chat_id_dict).filter(UserQuery.user_coin_name==CoinBase.id).\
            filter(or_(and_(UserQuery.query_minmax == "меньше", UserQuery.query_price > CoinBase.price_usd), and_(UserQuery.query_minmax == "больше", UserQuery.query_price < CoinBase.price_usd))).all()

        if len(coins) > 0:
            for coin in coins:
                coin_id = coin.__dict__['user_coin_name']
                coin_names = db_session.query(CoinBase).filter(CoinBase.id == coin_id).all()
                for coin_result in coin_names:
                    print(coin_result.__dict__['coin_name'])
                    bot.send_message(chat_id=user_chat_id_dict, text="Тревога!!! Твоя монета %s сейчас %s чем %s, она стоит - %s"
                                          % (coin_result.__dict__['coin_name'], coin.__dict__['query_minmax'], coin.__dict__['query_price'], coin_result.__dict__['price_usd']))
        else:
            print("Проверка не пройдена")

def is_float(string):
    try:
        float(string)
        return True
    except ValueError:
        return False

def query_bot(bot, update):

    
    user_chat_id = update['message']['chat']['id']

    text_chat = update['message']['text']
    coin_from_chat_list = text_chat.split(" ")
    try:
        coin_name = coin_from_chat_list[1].lower()
    except IndexError as err:
        print(err)
        update.message.reply_text("Что-то не так с названием валюты")

    try:
        coin_minmax = coin_from_chat_list[2].lower()
        print(coin_minmax)
        if (coin_minmax == "больше"):
            coin_minmax = coin_minmax
        elif coin_minmax == "меньше":
            coin_minmax = coin_minmax
        else:
            update.message.reply_text("Не правильно задаете параметры")
            return
    except IndexError as err:
        print(err)
        update.message.reply_text("Не правильно задаете параметры")

    try:
        coin_price = coin_from_chat_list[3]
        if is_float(coin_price):
            coin_price = coin_price 
        else:
            update.message.reply_text("Что-то не так с ценой")
            return
    except IndexError as err:
        print(err)
        update.message.reply_text("Что-то не так с ценой")

    try:
        coin = db_session.query(CoinBase).filter(CoinBase.coin_name == coin_name).first()
    except IndexError as err:
        print(err)
        update.message.reply_text("Что-то пошло не так!")

    if not coin:
        text = "Такой валюты нет"
        update.message.reply_text(text)
        return

    user = db_session.query(User).filter(User.id_user_chat==user_chat_id).first()

    if not user:
        text = "Такого пользователя нет"
        update.message.reply_text(text)
        return
    check_query = db_session.query(UserQuery).join(User).join(CoinBase).\
    filter(User.id==user.id, CoinBase.id==coin.id, UserQuery.query_minmax == coin_minmax).first()

    if not check_query:
        user_query = UserQuery(user.id, coin.id, coin_minmax, coin_price, datetime.utcnow())
        print(user_query)
        db_session.add(user_query)
        db_session.commit()
    else:
        user_query = db_session.query(UserQuery).join(User).join(CoinBase).\
        filter(User.id==user.id, CoinBase.id==coin.id, UserQuery.query_minmax == coin_minmax).first()
        user_query.query_price = coin_price
        db_session.add(user_query)
        db_session.commit()
        text = "Такой запрос уже был, интересующее Вас значение обновлено"
        update.message.reply_text(text)
        return

    my_text = """{} {}, ваш запрос добавлен!

    """.format(update.message.chat.first_name, update.message.chat.last_name)
    update.message.reply_text(my_text)

def start_bot(bot, update):
    author = User(update['message']['chat']['first_name'], update['message']['chat']['last_name'], update['message']['chat']['id'])
    print(author)

    chat_id = update['message']['chat']['id']
    r = ReplyKeyboardMarkup([["/help"],
                            ["/db"],
                            ["/check"],
                            ["/all"]])
    bot.send_message(chat_id=chat_id, text="^_^", reply_markup=r)
    try:
        db_session.add(author)
        db_session.commit()
        my_text = """Привет {} {}!

        я простой бот и пока понимаю только команды: 

        /help - список возможных комманд.

        /db - обновить базу данных валюты.

        /query [Имя валюты] [больще/меньше] [цена] - добавляет ваш запрос,
        в случае наличия такого же запроса, обновляет цену. 
        *Пример: /query Bitcoin больше 1234,5.

        /delete [имя валюты]* - удаляет ваши запросы / *запросы конкретной валюты

        /now [Имя валюты] - проверяет цену на валюту сейчас
        *Пример: /now Bitcoin.

        /all - список доступной валюты

        /check - проверяет Ваши запросы.


        """.format(update.message.chat.first_name, update.message.chat.last_name)
        update.message.reply_text(my_text)

    except IntegrityError:
        print("Такой юзер уже есть \n")
        db_session.rollback()
        my_text = """{} {}, Вы уже зарегистрированы!

        """.format(update.message.chat.first_name, update.message.chat.last_name)
        update.message.reply_text(my_text)

def bot_help(bot, update):

    my_text = """Привет {} {}!

    я простой бот и пока понимаю только команды: 

    /help - список возможных комманд

    /db - обновить базу данных валюты.

    /query [Имя валюты] [больще/меньше] [цена] 
    *Пример: Bitcoin больше 1234,5.

    /delete [имя валюты]* - удаляет ваши запросы / *запросы конкретной валюты

    /now [Имя валюты] - проверяет цену на валюту сейчас
    *Пример: /now Bitcoin.

    /all - список доступной валюты

    /check - проверяет Ваши запросы.


    """.format(update.message.chat.first_name, update.message.chat.last_name)
    update.message.reply_text(my_text)

def talk_to_me(bot, update):
    my_text = "Так это не работает, рекомендую воспользоваться командой /help"
    update.message.reply_text(my_text)
    user_text = update.message.text 
    print("Пользователь написал: %s " % user_text)

def callback_30(bot, job):
    bot.send_message(chat_id='192967689',
                    text='A single message with 30s delay')

def check_now(bot, update):
    data = get_bit("https://api.coinmarketcap.com/v1/ticker/?limit=10")
    user_chat_id = update['message']['chat']['id']
    text_chat = update['message']['text']
    coin_from_chat_list = text_chat.split(" ")
    coin_name = coin_from_chat_list[1].lower()
    for data_coin in data:
        name_coin = data_coin['name']
        name_coin_lower = name_coin.lower()
        price_coin = data_coin['price_usd']
        if name_coin_lower == coin_name:
            my_text = "Цена на {} сейчас {}".format(name_coin, price_coin)
            update.message.reply_text(my_text)

        else:
            print('Что-то пошло не так')
        
def all_coins(bot, update):
    data = get_bit("https://api.coinmarketcap.com/v1/ticker/?limit=10")
    all_coins_1 =[]
    for data_coin in data:
        name_coin = data_coin['name']
        all_coins_1.append(name_coin)
    print(all_coins_1)
    my_text = str(all_coins_1)
    update.message.reply_text('\n'.join(all_coins_1))

def delete(bot, update):
    text_chat = update['message']['text']
    coin_from_chat_list = text_chat.split(" ")
    coin_name = coin_from_chat_list[1].lower()
    user_chat_id = update['message']['chat']['id']
    coins = db_session.query(UserQuery).join(CoinBase).join(User).\
        filter(User.id_user_chat==user_chat_id).\
        filter(CoinBase.coin_name==coin_name).all()
    if len(coins) > 0:
        if not coin_name:
            print(111)
            coins = db_session.query(UserQuery).join(User).join(CoinBase).filter(User.id_user_chat==user_chat_id).all()
            for coins_del in coins:
                db_session.delete(coins_del)
            db_session.commit()
        else:
            print(222)
            for coins_del in coins:

                db_session.delete(coins_del)

            db_session.commit()
    else:
        print("@#!$!@")
        my_text = '''Такого запроса нет. ¯\_(ツ)_/¯'''
        update.message.reply_text(my_text)

def main():
    updtr = Updater(API_file.TELEGRAM_API_KEY)
    updtr.dispatcher.add_handler(CommandHandler("start", start_bot))
    updtr.dispatcher.add_handler(CommandHandler("db", db_update, pass_job_queue=True))
    updtr.dispatcher.add_handler(CommandHandler("query", query_bot))
    updtr.dispatcher.add_handler(CommandHandler("check", coin_check))
    updtr.dispatcher.add_handler(CommandHandler("help", bot_help))
    updtr.dispatcher.add_handler(CommandHandler("now", check_now))
    updtr.dispatcher.add_handler(CommandHandler("all", all_coins))
    updtr.dispatcher.add_handler(CommandHandler("delete", delete))
    updtr.dispatcher.add_handler(MessageHandler(Filters.text, talk_to_me))   
    u = Updater("418753388:AAH06yhJzVGIEIoKyWqQskZogq4nc9j6Pqk")
    j = u.job_queue
    j.run_once(callback_30, 1)
    updtr.start_polling()
    updtr.idle()

if __name__ == "__main__":
    logging.info("bot started")
    print("start huyart")
    u = Updater(API_file.TELEGRAM_API_KEY)
    j = u.job_queue
    j.run_once(callback_30, 1)
    main()