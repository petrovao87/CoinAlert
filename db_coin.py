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


if __name__ == "__main__":
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)