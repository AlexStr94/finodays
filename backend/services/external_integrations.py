import json
import os
from datetime import date, datetime, timedelta, timezone
from typing import List

import aiohttp
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession

from cashbacker.casbacker import categorizer, cashbacker
from core.config import BASE_DIR
from .db import (account_crud, card_crud, cashback_crud, transaction_crud,
                 user_cashback_crud)
from models import base as models
from schemas import base as schemas


load_dotenv(os.path.join(BASE_DIR, ".env"))


async def authenticate_user(
    username: str,
    password: str
) -> schemas.User | None:
    """
    Эмуляция получения информации о
    пользователи с сайта госуслуг
    """
    url = os.getenv('GET_USER_FROM_GOSUSLUGI_LINK')

    data = {
        'username': username,
        'password': password
    }

    async with aiohttp.ClientSession(trust_env = True) as session:
        async with session.post(url, json=data) as response:
            if response.status == 200:
                user_dict = json.loads(await response.text())
                user_dict['gosuslugi_id'] = user_dict.get('id')

                return schemas.User(**user_dict)
    
    return None


async def get_user_by_photo(photo: bytes, photo_name: str)-> schemas.User:
    """
        Эмуляция получения информации о пользователи из ЕБС
        по фото
    """
    url = os.getenv('GET_USER_ACOOUNTS_FROM_EBS_LINK')

    formdata = aiohttp.FormData()
    formdata.add_field('file_in', photo, filename=photo_name)

    async with aiohttp.ClientSession(trust_env = True) as session:
        async with session.post(url, data=formdata) as response:
            if response.status == 200:
                user_dict = json.loads(await response.text())
                user_dict['gosuslugi_id'] = user_dict.get('id')

                return schemas.User(**user_dict)
    
    return None


async def get_accounts(gosuslugi_id: str) -> List[schemas.RawAccount] | None:
    """
    Эмуляция получения информации о
    счетах и картах пользователя от НСПК
    """

    url = os.getenv('GET_USER_ACOOUNTS_FROM_NSPK_LINK')
    url = f'{url}?user_id={gosuslugi_id}'

    async with aiohttp.ClientSession(trust_env = True) as session:
        async with session.get(url) as response:
            if response.status == 200:
                accounts = json.loads(await response.text())
                return [
                    schemas.RawAccount(**account)
                    for account in accounts
                ]
    
    return None


async def get_account_cashbacks(
    account_number: str,
    month: date
) -> schemas.RawAccountCashbacks | None:
    url = os.getenv('GET_ACCOUNT_CASHBACKS_LINK')

    data = {
        'account_number': account_number,
        'month': month.strftime('%Y-%m-%d')
    }

    async with aiohttp.ClientSession(trust_env = True) as session:
        async with session.post(url, json=data) as response:
            if response.status == 200:
                cashbacks_dict = json.loads(await response.text())
                return schemas.RawAccountCashbacks(**cashbacks_dict)

    return None


async def create_or_update_account_in_db(
    db: AsyncSession,
    account: schemas.RawAccount,
    user_id: int,
    month: date
):  
    account_in_db = await account_crud.get_or_create(
        db=db,
        obj_in=schemas.AccountCreate(
            number=account.number,
            bank=account.bank,
            user_id=user_id
        )
    )
    for card in account.cards:
        await card_crud.get_or_create(
            db=db,
            obj_in=schemas.CardCreate.create_from_raw_card(
                raw_card=card, account_id=account_in_db.id
            )
        )
    

    account_cashbacks_info: schemas.RawAccountCashbacks | None = None

    account_cashbacks_info = await get_account_cashbacks(
        account_number=account_in_db.number,
        month=month
    )

    if not account_cashbacks_info:
        return
    
    if account_cashbacks := account_cashbacks_info.cashbacks:
        account_cashbacks_in_db: List[models.Cashback] = [
            await cashback_crud.get_or_create(
                db,
                schemas.CashbackCreate.create_from_raw_cashback(cashback)
            )
            for cashback in account_cashbacks
        ]
        raw_user_cashbacks = zip(account_cashbacks, account_cashbacks_in_db)
        user_cashbacks_in_db: List[models.UserCashback] = [
            await user_cashback_crud.get_or_create(
                db, schemas.UserCashbackCreate(
                    account_id=account_in_db.id,
                    cashback_id=raw_user_cashback[1].id,
                    month=month,
                    value=raw_user_cashback[0].value,
                    status=True
                )
            ) for raw_user_cashback in raw_user_cashbacks
        ]


async def create_or_update_accounts_in_db(
    db: AsyncSession,
    accounts: List[schemas.RawAccount],
    user: models.User,
    month: date
):
    for account in accounts:
        await create_or_update_account_in_db(
            db=db,
            account=account,
            user_id=user.id,
            month=month
        )


async def update_account_transactions(
    db: AsyncSession, account: models.Account
) -> None:
    # Будем обновлять не чаще чем раз в 30 минут
    last_update: datetime | None = account.transations_update_time
    now = datetime.now().replace(tzinfo=timezone.utc)
    
    if last_update and (now - last_update > timedelta(minutes=30)):
        return
    
    last_transation_time = account.last_transation_time
    if last_transation_time:
        last_transation_time = last_transation_time.isoformat()
    url = os.getenv('GET_ACCOUNT_TRANSACTIONS_LINK')
    data = {
        'account_number': account.number,
        'start_datetime': last_transation_time
    }
    async with aiohttp.ClientSession(trust_env = True) as session:
        async with session.post(url, json=data) as response:
            if response.status == 200:
                # обновляем время последнего обновления транзакций
                account = await account_crud.update(
                    db=db,
                    obj_in=schemas.AccountUpdate(
                        id=account.id,
                        transations_update_time=datetime.utcnow()
                    )
                )
                _dict = json.loads(await response.text())
                raw_account_transactions = schemas.RawAccountTransactions(**_dict)
                
                transactions_categories = categorizer.get_topics_name(
                    product_names=[
                        transaction.name
                        for transaction in raw_account_transactions.transactions
                    ]
                )
                transactions_info = zip(raw_account_transactions.transactions, transactions_categories)
                transactions = [
                    schemas.TransactionCreate(
                        time=transaction[0].time,
                        bank_id=transaction[0].id,
                        name=transaction[0].name,
                        value=transaction[0].value,
                        account_id=account.id,
                        category=transaction[1]
                    )
                    for transaction in transactions_info
                ]
                if len(transactions) > 0:
                    await transaction_crud.bulk_create(
                        db=db, objs_in=transactions
                    )

                    last_transation_time = raw_account_transactions \
                        .transactions[-1].time.replace(tzinfo=timezone.utc)
                    account = await account_crud.update(
                        db=db,
                        obj_in=schemas.AccountUpdate(
                            id=account.id,
                            last_transation_time=last_transation_time
                        )
                    )

                
async def update_user_transactions(db: AsyncSession, user_id: int):
    accounts: List[models.Account] = await account_crud.filter_by(
        db=db, user_id=user_id
    )

    for account in accounts:
        await update_account_transactions(db=db, account=account)
