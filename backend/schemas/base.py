from datetime import date
from typing import List
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class User(BaseModel):
    first_name: str
    surname: str
    gosuslugi_id: str
    ebs: bool


class FullUser(User):
    id: int

class GosuslugiUser(BaseModel):
    first_name: str
    # middle_name: str
    surname: str
    gosuslugi_id: str
    ebs: bool


class LiteCard(BaseModel):
    bank: str
    card_number: str


class Card(LiteCard):
    user_id: int


class Cashback(BaseModel):
    product_type: str
    value: int


class UserCashback(BaseModel):
    card_id: int
    cashback_id: int
    month: date
    status: bool


class CardWithCashback(BaseModel):
    bank: str
    last_four_digits: str
    cashback: List[Cashback] | None # если кешбек не выбран или не может быть выбран


class FullCardWithCashback(CardWithCashback):
    card_id: int
    can_choose: bool


class CardList(BaseModel):
    cards: List[FullCardWithCashback]


class MonthCashback(BaseModel):
    month: date
    cashback: List[Cashback]


class TerminalResponse(BaseModel):
    name: str
    surname: str
    # middlename: str
    cards: List[CardWithCashback]