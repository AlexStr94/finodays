import asyncio
import csv
import os
from datetime import date, datetime, timedelta
from random import choice, choices, randint, randrange
from string import digits
from typing import List

from dateutil import relativedelta
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from models import base as models
from schemas import base as schemas
from services.db import (bank_crud, card_crud, cashback_crud, transaction_crud,
                         user_cashback_crud, user_crud)

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))

database_dsn = os.getenv('DATABASE_DSN')

CASHBACK_CATEGORIES = [
    'автозапчасти', 'видеоигры', 'напитки', 'продукты питания',
    'закуски и приправы', 'аквариум', 'одежда', 'уборка', 'электроника'
]

engine = create_async_engine(
    database_dsn, echo=True, future=True
)
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


def generate_card_number() -> str:
    return '2200' + ''.join(choices(digits, k=12))


async def generate_card_info(db: AsyncSession, user_id: int, bank_id: int) -> schemas.CardCreate:
    while True:
        card_number = generate_card_number()
        card: models.Card | None = await card_crud.get(
            db=db, card_number=card_number
        )
        if not card:
            return schemas.CardCreate(
                user_id=user_id,
                bank_id=bank_id,
                card_number=card_number
            )


def generate_random_date(start_day: date, num_of_days: int) -> date:
    random_num = randrange(num_of_days)
    return start_day + timedelta(days=random_num)


async def init_mock_data() -> None:
    async with async_session() as session:
        cashbacks: List[models.Cashback] = []
        for category in CASHBACK_CATEGORIES:
            cashback = await cashback_crud.create(
                db=session,
                obj_in=schemas.CashbackCreate(
                    product_type=category
                )
            )
            cashbacks.append(cashback)

        banks_not_in_system: List[models.Bank] = []
        banks_in_system: List[models.Bank] = []

        with open(f'{CURRENT_DIR}/data/banks.csv', 'r', encoding='utf-8', newline='') as csvfile:
            rows = csv.reader(csvfile)
            for row in rows:
                bank = schemas.BankCreate(
                    name=row[0],
                    in_system=(row[1] == 'true'),
                    allow_cashback_choose=(row[2] == 'true')
                )
                bank_in_db = await bank_crud.create(session, bank)
                if bank_in_db.name == 'Центр-инвест':
                    main_bank = bank_in_db
                elif bank_in_db.in_system:
                    banks_in_system.append(bank_in_db)
                else:
                    banks_not_in_system.append(bank_in_db)

        num_of_banks_in_system: int = len(banks_in_system)
        num_of_banks_not_in_system: int = len(banks_not_in_system)

        with open(f'{CURRENT_DIR}/data/users.csv', 'r', encoding='utf-8', newline='') as csvfile:
            rows = csv.reader(csvfile)
            for row in rows:
                user = schemas.UserCreate(
                    first_name=row[0],
                    surname=row[1],
                    ebs=True,
                    gender=row[3],
                    birth_date=datetime.strptime(row[4], '%Y.%M.%d'),
                    sitizenship=row[5],
                    birth_place=row[6]
                )
                user_in_db: models.User = await user_crud.create(session, user)

                await card_crud.create(
                    db=session,
                    obj_in=await generate_card_info(
                        db=session,
                        user_id=user_in_db.id,
                        bank_id=main_bank.id
                    )
                )

                for i in range(0, randint(1, 2)):
                    bank_index = randint(0, num_of_banks_not_in_system-1)
                    await card_crud.create(
                        db=session,
                        obj_in=await generate_card_info(
                            db=session,
                            user_id=user_in_db.id,
                            bank_id=banks_not_in_system[bank_index].id
                        )
                    )

                user_cards_with_cashback: List[models.Card] = []

                for i in range(0, randint(1, 2)):
                    bank_index = randint(0, num_of_banks_in_system-1)
                    card: models.Card = await card_crud.create(
                        db=session,
                        obj_in=await generate_card_info(
                            db=session,
                            user_id=user_in_db.id,
                            bank_id=banks_in_system[bank_index].id
                        )
                    )

                    user_cards_with_cashback.append(card)

                today = date.today() 
                today = date(year=today.year, month=today.month, day=1)
                next_month = today  + relativedelta.relativedelta(months=1)
                
                for card in user_cards_with_cashback:
                    card_cashbacks = choices(cashbacks, k=3)
                    for cashback in card_cashbacks:
                        await user_cashback_crud.create(
                            db=session,
                            obj_in=schemas.UserCashbackCreate(
                                card_id=card.id,
                                cashback_id=cashback.id,
                                value=randint(3, 10),
                                month=today
                            )
                        )
                        await user_cashback_crud.create(
                            db=session,
                            obj_in=schemas.UserCashbackCreate(
                                card_id=card.id,
                                cashback_id=cashback.id,
                                value=randint(3, 10),
                                month=next_month
                            )
                        )

        # генерируем транзакции для карт
        with open(f'{CURRENT_DIR}/data/transactions.csv', 'r', encoding='utf-8', newline='') as csvfile:
            cards: List[models.Card] = await card_crud.all(db=session)
            rows = csv.reader(csvfile)
            for row in rows:
                card = choice(cards)
                await transaction_crud.create(
                    db=session,
                    obj_in=schemas.TransactionCreate(
                        name=row[0],
                        time=generate_random_date(today, 60),
                        value=int(row[1]),
                        card_id=card.id
                    )
                )


if __name__ == '__main__':
    asyncio.run(init_mock_data())
