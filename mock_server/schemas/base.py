from datetime import date
from typing import List

from pydantic import BaseModel


class BankCreate(BaseModel):
    name: str
    in_system: bool
    allow_cashback_choose: bool


class UserCreate(BaseModel):
    first_name: str
    surname: str
    ebs: bool
    gender: str
    birth_date: date
    sitizenship: str
    birth_place: str


class User(UserCreate):
    id: int

    class Config:
        orm_mode = True


class CardCreate(BaseModel):
    user_id: int
    bank_id: int
    card_number: str


class Card(BaseModel):
    bank: str
    card_number: str


class CardCashback(BaseModel):
    product_type: str
    value: int


class CardWithCashbacks(Card):
    month: date
    cashbacks: List[CardCashback]


class TransactionCreate(BaseModel):
    name: str
    time: date
    value: int
    card_id: int


class Transaction(BaseModel):
    id: int
    name: str
    time: date
    value: int

    class Config:
        orm_mode = True
    

class CardWithCashbacksandTransactions(CardWithCashbacks):
    transactions: List[Transaction]


class CashbackCreate(BaseModel):
    product_type: str


class UserCashbackCreate(BaseModel):
    card_id: int
    cashback_id: int
    value: int
    month: date


class UserCredentials(BaseModel):
    username: str
    password: str