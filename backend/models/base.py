from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.types import TIMESTAMP

from db.db import Base


class User(Base):
    __tablename__ = 'users'
    __mapper_args__ = {"eager_defaults": True}
    id = Column(Integer, primary_key=True)
    first_name = Column(String(100), nullable=False)
    surname = Column(String(100), nullable=False)
    gosuslugi_id = Column(String(16), unique=True)
    ebs = Column(Boolean)
    accounts = relationship('Account', back_populates='user')


class Account(Base):
    __tablename__ = 'accounts'
    __mapper_args__ = {"eager_defaults": True}
    id = Column(Integer, primary_key=True)
    number = Column(String(100), nullable=False, unique=True)
    bank = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship('User', back_populates='accounts')
    cards = relationship('Card', back_populates='account')
    cashbacks = relationship('UserCashback', back_populates='account')
    transactions = relationship('Transaction', back_populates='account')
    last_transation_time = Column(type_=TIMESTAMP(timezone=True)) # для обновления транзакций только с определенной даты
    transations_update_time = Column(type_=TIMESTAMP(timezone=True)) # для обновления транзакций только с определенной даты


class Card(Base):
    __tablename__ = 'cards'
    __mapper_args__ = {"eager_defaults": True}
    id = Column(Integer, primary_key=True)
    card_number = Column(String(20), unique=True)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    account = relationship('Account', back_populates='cards', cascade='delete, merge, save-update')
    # Можно добавить срок действия, чтобы не показывать старые карты пользователя.
    # Также можно статус открыта/закрыта


class Cashback(Base):
    __tablename__ = 'cashbacks'
    __mapper_args__ = {"eager_defaults": True}
    id = Column(Integer, primary_key=True)
    product_type = Column(String(100), nullable=False, unique=True)
    accounts = relationship('UserCashback', back_populates='cashback')


class UserCashback(Base):
    __tablename__ = 'usercashbacks'
    __mapper_args__ = {"eager_defaults": True}
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    account = relationship('Account', back_populates='cashbacks', cascade='delete, merge, save-update')
    cashback_id = Column(Integer, ForeignKey('cashbacks.id'), nullable=False)
    cashback = relationship('Cashback', back_populates='accounts', cascade='delete, merge, save-update')
    month = Column(Date, nullable=False)
    value = Column(Integer)
    status = Column(Boolean, nullable=False)
    __table_args__ = (
        UniqueConstraint(
            'account_id', 'cashback_id', 'month'
        ),
    )


class Transaction(Base):
    __tablename__ = 'transactions'
    __mapper_args__ = {"eager_defaults": True}
    id = Column(Integer, primary_key=True)
    bank_id = Column(Integer, unique=True) # id транзакции в банке, доп. защита от дублей
    name = Column(String(300), nullable=False)
    value = Column(Integer, nullable=False)
    time = Column(type_=TIMESTAMP(timezone=True))
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    account = relationship('Account', back_populates='transactions', cascade='delete, merge, save-update')
    category = Column(String(100), nullable=True)
