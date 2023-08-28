from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date
from sqlalchemy.orm import relationship

from db.db import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    first_name = Column(String(100), nullable=False)
    surname = Column(String(100), nullable=False)
    gosuslugi_id = Column(String(16), unique=True)
    ebs = Column(Boolean)
    cards = relationship('Card', back_populates='user', cascade='delete, merge, save-update')


class Card(Base):
    __tablename__ = 'cards'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship('User', back_populates='cards')
    bank = Column(String(100), nullable=False)
    card_number = Column(Integer, unique=True)
    cashbacks = relationship('UserCashback', back_populates='card', cascade='delete, merge, save-update')


class Cashback(Base):
    __tablename__ = 'cashbacks'
    id = Column(Integer, primary_key=True)
    product_type = Column(String(100), nullable=False)
    value = Column(Integer)
    cards = relationship('UserCashback', back_populates='cashback', cascade='delete, merge, save-update')


class UserCashback(Base):
    __tablename__ = 'usercashbacks'
    id = Column(Integer, primary_key=True)
    card_id = Column(Integer, ForeignKey('cards.id'), nullable=False)
    card = relationship('Card', back_populates='cashbacks')
    cashback_id = Column(Integer, ForeignKey('cashbacks.id'), nullable=False)
    cashback = relationship('Cashback', back_populates='cards')
    month = Column(Date, nullable=False)
    status = Column(Boolean, nullable=False)
