from datetime import date, timezone
from random import choice
from typing import List

from fastapi import APIRouter, Depends, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.db import get_session
from exceptions import base as exceptions
from models import base as models
from schemas import base as schemas
from services.db import (account_crud, transaction_crud, user_cashback_crud,
                         user_crud)

router = APIRouter()


@router.post(
    '/get_user/',
    status_code=status.HTTP_200_OK,
    response_model=schemas.User
)
async def get_user(
    user_credentials: schemas.UserCredentials,
    db: AsyncSession = Depends(get_session)
) -> schemas.User:
    users: List[models.User] = await user_crud.all(db)
    user: models.User = choice(users)
    return schemas.User.from_orm(user)


@router.post(
    '/get_user_by_photo/',
    status_code=status.HTTP_200_OK,
    response_model=schemas.User
)
async def get_user_by_photo(
    file_in: UploadFile,
    db: AsyncSession = Depends(get_session)
) -> schemas.User:
    users: List[models.User] = await user_crud.all(db)
    user: models.User = choice(users)
    return schemas.User.from_orm(user)


@router.get( 
    '/get_user_accounts/',
    status_code=status.HTTP_200_OK,
    response_model=List[schemas.Account]
)
async def get_user_accounts(
    user_id: int,
    db: AsyncSession = Depends(get_session)
) -> List[schemas.Account]:
    user: models.User | None = await user_crud.get(db, id=user_id)
    if not user:
        raise exceptions.UserNotFoundException
    accounts: List[models.Account] = await account_crud.filter_by(
        db=db, with_cards=True,
        with_bank=True, user_id=user_id
    )

    return [
        schemas.Account(
            bank=account.bank.name,
            number=account.number,
            cards=[
                schemas.Card(
                    card_number=card.card_number
                )
                for card in account.cards
            ]
        )
        for account in accounts
    ]


@router.post(
    '/get_account_cashbacks/',
    status_code=status.HTTP_200_OK,
    response_model=schemas.AccountWithCashbacks
)
async def get_account_cashback(
    account: schemas.AccountRequest,
    db: AsyncSession = Depends(get_session)
) -> schemas.AccountWithCashbacks:
    cashbacks = await user_cashback_crud.account_cashbacks(
        db=db,
        account_number=account.account_number,
        month=account.month
    )
    
    return schemas.AccountWithCashbacks(
        month=account.month,
        cashbacks=[
            schemas.AccountCashback(
                product_type=cashback.cashback.product_type,
                value=cashback.value
            )
            for cashback in cashbacks
        ]
    )


@router.post(
    '/get_account_transactions/',
    status_code=status.HTTP_200_OK,
    response_model=schemas.AccountWithTransactions
)
async def get_account_transactions(
    data: schemas.TransactionsRequest,
    db: AsyncSession = Depends(get_session)
) -> schemas.AccountWithTransactions:
    transactions = await transaction_crud.get_account_transactions(
        db=db, account_number=data.account_number,
        start_datetime=data.start_datetime
    )

    return schemas.AccountWithTransactions(
        number=data.account_number,
        transactions=[
            schemas.Transaction.from_orm(transaction)
            for transaction in transactions
        ]
    )
