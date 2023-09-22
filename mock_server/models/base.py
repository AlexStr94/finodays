from sqlalchemy import (Boolean, Column, Date, DateTime, ForeignKey, Integer,
                        String)
from sqlalchemy.orm import relationship

from db.db import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    first_name = Column(String(100), nullable=False)
    surname = Column(String(100), nullable=False)
    ebs = Column(Boolean)
    gender = Column(String(1), nullable=False)
    birth_date = Column(Date, nullable=False)
    sitizenship = Column(String(50), nullable=False)
    birth_place = Column(String(100), nullable=False)
    cards = relationship('Card', back_populates='user')


class Bank(Base):
    __tablename__ = 'banks'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    in_system = Column(Boolean)
    allow_cashback_choose = Column(Boolean)
    cards = relationship('Card', back_populates='bank')



class Card(Base):
    __tablename__ = 'cards'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship('User', back_populates='cards', cascade='delete, merge, save-update')
    bank_id = Column(Integer, ForeignKey('banks.id'), nullable=False)
    bank = relationship('Bank', back_populates='cards', cascade='delete, merge, save-update')
    card_number = Column(String(20), unique=True)
    cashbacks = relationship('UserCashback', back_populates='card')
    transactions = relationship('Transaction', back_populates='card')
    # Можно добавить срок действия, чтобы не показывать старые карты пользователя.
    # Также можно статус открыта/закрыта


class Cashback(Base):
    __tablename__ = 'cashbacks'
    id = Column(Integer, primary_key=True)
    product_type = Column(String(100), nullable=False)
    cards = relationship('UserCashback', back_populates='cashback')


class UserCashback(Base):
    __tablename__ = 'usercashbacks'
    id = Column(Integer, primary_key=True)
    card_id = Column(Integer, ForeignKey('cards.id'), nullable=False)
    card = relationship('Card', back_populates='cashbacks', cascade='delete, merge, save-update')
    cashback_id = Column(Integer, ForeignKey('cashbacks.id'), nullable=False)
    cashback = relationship('Cashback', back_populates='cards', cascade='delete, merge, save-update')
    value = Column(Integer)
    month = Column(Date, nullable=False)


class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True)
    name = Column(String(300), nullable=False)
    value = Column(Integer, nullable=False)
    time = Column(DateTime, nullable=False)
    card_id = Column(Integer, ForeignKey('cards.id'), nullable=False)
    card = relationship('Card', back_populates='transactions', cascade='delete, merge, save-update')
