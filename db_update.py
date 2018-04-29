from db_coin import db_session, CoinBase, User, UserQuery
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import requests
import json
from sqlalchemy import exc
from sqlalchemy.exc import IntegrityError
from datetime import datetime, date, time
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy import or_


def get_bit(url):
    result = requests.get(url)
    if result.status_code == 200:
        return(result.json())
    else:
        print("Тебя послали")

def _up():
    data = get_bit("https://api.coinmarketcap.com/v1/ticker/?limit=10")

    #job_queue.run_repeating(callback_30, interval=10, first=0)

    for data_coin in data:
        
        name_coin = data_coin['name']
        price_coin = data_coin['price_usd']
        print(price_coin)
        print(name_coin)
        coin_in_db = db_session.query(CoinBase).filter(CoinBase.coin_name == name_coin.lower()).first()
        #import ipdb; ipdb.set_trace()


        if not coin_in_db:
            coin = CoinBase(data_coin['name'].lower(), data_coin['price_usd'], datetime.utcnow())
            db_session.add(coin)
            db_session.commit()
            print("Добавлено значение - %s" % name_coin)

        else:
            print('обновляю значение')
            coin_in_db.price_usd = float(price_coin)
            coin_in_db.query_date = datetime.utcnow()
            #import ipdb; ipdb.set_trace()
            db_session.add(coin_in_db)
            db_session.commit()



if __name__ == "__main__":
    print("update base")


    #main()
    _up()
    #send_messa