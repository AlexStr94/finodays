from datetime import date, datetime
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


class RawCard(BaseModel):
    card_number: str


class RawAccount(BaseModel):
    bank: str
    number: str
    cards: List[RawCard]


class RawCashback(BaseModel):
    product_type: str
    value: int


class RawTransactions(BaseModel):
    id: int
    name: str
    time: datetime
    value: int


class RawAccountCashbacks(BaseModel):
    month: date
    cashbacks: List[RawCashback]


class RawAccountTransactions(BaseModel):
    number: str
    transactions: List[RawTransactions]


class CardCreate(BaseModel):
    card_number: str
    account_id: int

    @classmethod
    def create_from_raw_card(cls, raw_card: RawCard, account_id: int):
        card_dict = raw_card.dict()
        card_dict['account_id'] = account_id
        return cls(**card_dict)


class AccountCreate(BaseModel):
    number: str
    bank: str
    user_id: int


class AccountUpdate(BaseModel):
    id: int
    last_transation_time: datetime | None = None
    transations_update_time: datetime | None = None


class CashbackCreate(BaseModel):
    product_type: str

    @classmethod
    def create_from_raw_cashback(cls, raw_cashback: RawCashback):
        return cls(product_type=raw_cashback.product_type)


class UserCashback(BaseModel):
    account_id: int
    cashback_id: int
    month: date
    value: int
    status: bool


class UserCashbackCreate(UserCashback):
    pass


class UserCashbackUpdate(BaseModel):
    id: int
    status: bool


class Transaction(BaseModel):
    time: datetime
    name: str
    value: int
    category: str

    class Config:
        orm_mode = True

class TransactionCreate(Transaction):
    bank_id: int
    account_id: int


class Cashback(RawCashback):
    pass

    class Config:
        orm_mode = True


class Card(BaseModel):
    last_four_digits: str


class CashbacksForChoose(BaseModel):
    account_number: str
    bank: str
    can_choose_cashback: bool
    cashbacks: List[Cashback]


class AccountWithCardsAndCashbacks(CashbacksForChoose):
    cards: List[Card]


class AccountWithTransactions(BaseModel):
    account_number: str
    bank: str
    transactions: List[Transaction]


class CardWithCashback(BaseModel):
    bank: str
    last_four_digits: str
    cashbacks: List[Cashback | RawCashback] | None # если кешбек не выбран или не может быть выбран



class MonthCashback(BaseModel):
    account_number: str
    month: date
    cashback: List[Cashback]


class TerminalResponse(BaseModel):
    name: str
    surname: str
    # middlename: str
    cards: List[CardWithCashback]