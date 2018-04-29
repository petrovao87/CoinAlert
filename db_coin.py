from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime, ForeignKey, Table
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///coin_db.db')

db_session = scoped_session(sessionmaker(bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    id_user_chat = Column(String(120), unique=True)
    coins = relationship("CoinBase", secondary='user_query')

    def __init__(self, first_name=None, last_name=None, id_user_chat=None):
        self.first_name = first_name
        self.last_name = last_name
        self.id_user_chat = id_user_chat


class UserQuery(Base):
    __tablename__ = 'user_query'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user_coin_name = Column(Integer, ForeignKey('coin_base.id'))
    query_minmax = Column(String(50))
    query_price = Column(Float)
    user_query_date = Column(DateTime)

    #coins = relationship("CoinBase", secondary='user_assoc_tab')

    def __init__(self, user_id=None, user_coin_name=None, query_minmax=None, query_price=None, user_query_date=None):
        self.user_id = user_id
        self.user_coin_name = user_coin_name
        self.query_minmax = query_minmax
        self.query_price = query_price
        self.user_query_date = user_query_date


class CoinBase(Base):
    __tablename__ = 'coin_base'
    id = Column(Integer, primary_key=True)
    coin_name = Column(String(50), unique=True)
    price_usd = Column(Float)
    query_date = Column(DateTime)
    user = relationship("User", secondary='user_query')

    def __init__(self, coin_name=None, price_usd=None, query_date=None):
        self.coin_name = coin_name
        self.price_usd = price_usd
        self.query_date = query_date


#class UserCoin(Base):
#    __tablename__ = 'user_assoc_tab'
#    user_id = Column(Integer, ForeignKey('user_query.id'), primary_key=True)
    #query_minmax = Column(String(50), key='query_minmax')
    #query_price = Column(String(50))
#    coin_base_id = Column(Integer, ForeignKey('coin_base.id'), primary_key=True)


# association_table = Table('user_assoc_tab', Base.metadata,
#                           Column('user_id', Integer, ForeignKey('user_query.id')),
#                           Column('query_minmax', String(50), key='query_minmax'),
#                           Column(String(50)),
#                           # Column('user_chat_id', Integer, ForeignKey('user_query.user_id')),
#                           # Column('query_coin_name', String(50), ForeignKey('user_query.coin_name')),
#                           # Column('query_price', Integer, ForeignKey('user_query.query_price')),
#                           Column(Integer, ForeignKey('coin_base.id'))
#                           # Column('coin_id', String(50), ForeignKey('coin_base.coin_name')),
#                           # Column('price_usd', String(50), ForeignKey('coin_base.price_usd'))
#                           )

if __name__ == "__main__":
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    # добавляем валюту
    #coin = CoinBase(coin_name='coin1', price_usd='12', query_date=datetime.now())
    # и пользователя (пока они не связаны)
    #user = UserQuery(user_id="123456")
    # теперь пользователю добавим валюту
    #user.coins = [coin]
    #db_session.add(user)
    #db_session.commit()
    #coin_link = db_session.query(UserCoin).filter(UserQuery.id == user.id, CoinBase.id == coin.id).first()
    #coin_link.query_minmax = '1222'
    #db_session.add(coin_link)
    #db_session.commit()