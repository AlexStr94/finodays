import asyncio
import csv
import os
from datetime import date, datetime, timedelta, timezone
from random import choice, choices, randint, randrange, sample
from string import digits
from typing import List

from dateutil import relativedelta
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from models import base as models
from schemas import base as schemas
from services.db import (account_crud, bank_crud, card_crud, cashback_crud, transaction_crud,
                         user_cashback_crud, user_crud)

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))

database_dsn = os.getenv(
    'DATABASE_DSN',
    'postgresql+asyncpg://mock:mock@localhost:5432/mock'
)

CASHBACK_CATEGORIES = [
    'автозапчасти', 'видеоигры', 'напитки', 'продукты питания',
    'закуски и приправы', 'аквариум', 'одежда', 'уборка',
    'электроника', 'образование'
]

engine = create_async_engine(
    database_dsn, echo=True, future=True
)
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


def generate_account_number() -> str:
    return '4081' + ''.join(choices(digits, k=16))


def generate_card_number() -> str:
    return '2200' + ''.join(choices(digits, k=12))


async def generate_account_info(
    db: AsyncSession,
    bank_id: int,
    user_id: int
) -> schemas.AccountCreate:
    while True:
        account_number = generate_account_number()
        account: models.Account | None = await account_crud.get(
            db=db, number=account_number
        )
        if not account:
            return schemas.AccountCreate(
                number=account_number,
                bank_id=bank_id,
                user_id=user_id
            )


async def generate_card_info(
    db: AsyncSession,
    account_id: int
) -> schemas.CardCreate:
    while True:
        card_number = generate_card_number()
        card: models.Card | None = await card_crud.get(
            db=db, card_number=card_number
        )
        if not card:
            return schemas.CardCreate(
                account_id=account_id,
                card_number=card_number
            )


def generate_random_datetime(
        start_day: datetime, num_of_days: int
    ) -> datetime:
    random_num = randrange(num_of_days)
    time = start_day + timedelta(
        days=random_num,
        hours=randint(1, 24),
        minutes=randint(1, 60),
        seconds=randint(1, 60)
    )
    return time.replace(tzinfo=timezone.utc)


async def init_mock_data() -> None:
    async with async_session() as session:
        # Создаем категории кэшбека в БД
        cashbacks: List[models.Cashback] = []
        for category in CASHBACK_CATEGORIES:
            cashback = await cashback_crud.create(
                db=session,
                obj_in=schemas.CashbackCreate(
                    product_type=category
                )
            )
            cashbacks.append(cashback)

        # Создаем банки в БД
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

        # Создаем пользователей, счета и карты пользователя
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

                # Генерируем счет и карты Центр-инвеста
                main_bank_account: models.Account = await account_crud.create(
                    db=session,
                    obj_in=await generate_account_info(
                        db=session,
                        bank_id=main_bank.id,
                        user_id=user_in_db.id,
                    )
                )
                for i in range(0, 2):
                    await card_crud.create(
                        db=session,
                        obj_in=await generate_card_info(
                            db=session,
                            account_id=main_bank_account.id
                        )
                    )

                # Генерируем счета и карты банков, не подключенных к системе
                for i in range(0, randint(1, 2)):
                    bank_index = randint(0, num_of_banks_not_in_system-1)
                    bank_account: models.Account = await account_crud.create(
                        db=session,
                        obj_in=await generate_account_info(
                            db=session,
                            bank_id=banks_not_in_system[bank_index].id,
                            user_id=user_in_db.id,
                        )
                    )
                    for i in range(0, randint(1, 2)):
                        await card_crud.create(
                            db=session,
                            obj_in=await generate_card_info(
                                db=session,
                                account_id=bank_account.id
                            )
                        )

                user_accounts_with_cashback: List[models.Card] = []

                # Генерируем счета и карты банков, подключенных к системе частично
                for i in range(0, randint(1, 2)):
                    bank_index = randint(0, num_of_banks_in_system-1)
                    bank_account = await account_crud.create(
                        db=session,
                        obj_in=await generate_account_info(
                            db=session,
                            bank_id=banks_in_system[bank_index].id,
                            user_id=user_in_db.id,
                        )
                    )
                    for i in range(0, randint(1, 2)):
                        await card_crud.create(
                            db=session,
                            obj_in=await generate_card_info(
                                db=session,
                                account_id=bank_account.id
                            )
                        )

                    user_accounts_with_cashback.append(bank_account)

                today = date.today() 
                today = date(year=today.year, month=today.month, day=1)
                next_month = today  + relativedelta.relativedelta(months=1)
                
                for account in user_accounts_with_cashback:
                    account_cashbacks: List[models.Cashback] = sample(cashbacks, k=3)
                    for cashback in account_cashbacks:
                        await user_cashback_crud.create(
                            db=session,
                            obj_in=schemas.UserCashbackCreate(
                                account_id=account.id,
                                cashback_id=cashback.id,
                                value=randint(3, 10),
                                month=today
                            )
                        )
                        await user_cashback_crud.create(
                            db=session,
                            obj_in=schemas.UserCashbackCreate(
                                account_id=account.id,
                                cashback_id=cashback.id,
                                value=randint(3, 10),
                                month=next_month
                            )
                        )

        # генерируем транзакции для счетов
        with open(f'{CURRENT_DIR}/data/transactions.csv', 'r', encoding='utf-8', newline='') as csvfile:
            accounts: List[models.Account] = await account_crud.all(db=session)
            rows = csv.reader(csvfile)
            today = date.today()
            start_transaction_datetime = datetime(
                year=today.year - 1,
                month=today.month,
                day=1
            )
            for index, row in enumerate(rows):
                account = choice(accounts)
                if index % 10 == 0:
                    time = datetime(
                        year=2023,
                        month=11,
                        day=choice([i for i in range(1,9)]),
                        hour=randint(1, 24),
                        minute=randint(1, 60),
                        second=randint(1, 60)
                    )
                else:
                    time = generate_random_datetime(
                        start_transaction_datetime,
                        365 + today.day
                    )
                await transaction_crud.create(
                    db=session,
                    obj_in=schemas.TransactionCreate(
                        name=row[0],
                        time=time,
                        value=int(row[1]),
                        account_id=account.id
                    )
                )


if __name__ == '__main__':
    asyncio.run(init_mock_data())
