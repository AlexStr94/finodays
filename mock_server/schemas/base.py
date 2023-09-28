from datetime import date, datetime
from typing import List

from pydantic import BaseModel


class BankCreate(BaseModel):
    name: str
    in_system: bool
    allow_cashback_choose: bool


class AccountCreate(BaseModel):
    number: str
    bank_id: int
    user_id: int


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
    card_number: str
    account_id: int


class Card(BaseModel):
    card_number: str


class Account(BaseModel):
    bank: str
    number: str
    cards: List[Card]


class AccountRequest(BaseModel):
    account_number: str
    month: date


class AccountCashback(BaseModel):
    product_type: str
    value: int


class AccountWithCashbacks(BaseModel):
    month: date
    cashbacks: List[AccountCashback]


class TransactionsRequest(BaseModel):
    account_number: str
    start_datetime: datetime | None


class TransactionCreate(BaseModel):
    name: str
    time: datetime
    value: int
    account_id: int


class Transaction(BaseModel):
    id: int
    name: str
    time: datetime
    value: int

    class Config:
        orm_mode = True


class AccountWithTransactions(BaseModel):
    number: str
    transactions: List[Transaction]


class CashbackCreate(BaseModel):
    product_type: str


class UserCashbackCreate(BaseModel):
    account_id: int
    cashback_id: int
    value: int
    month: date


class UserCredentials(BaseModel):
    username: str
    password: str