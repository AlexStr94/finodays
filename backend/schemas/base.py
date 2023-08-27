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


class Card(BaseModel):
    bank: str
    number: str