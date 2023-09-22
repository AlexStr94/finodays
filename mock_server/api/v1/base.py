from datetime import date
from typing import List
from random import choice

from fastapi import APIRouter, Depends, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.db import get_session
from exceptions import base as exceptions
from models import base as models
from services.db import card_crud, user_crud, user_cashback_crud, transaction_crud
from schemas import base as schemas 

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


@router.post( 
    '/get_user_cards/',
    status_code=status.HTTP_200_OK,
    response_model=List[schemas.Card]
)
async def get_user_cards(
    user_id: int,
    db: AsyncSession = Depends(get_session)
) -> List[schemas.Card]:
    user: models.User | None = await user_crud.get(db, id=user_id)
    if not user:
        raise exceptions.UserNotFoundException
    cards: List[models.Card] = await card_crud.filter_by(db, user_id=user_id)
    return [
        schemas.Card(
            bank=card.bank.name,
            card_number=card.card_number
        )
        for card in cards
    ]


@router.post(
    '/get_card_cashback/',
    status_code=status.HTTP_200_OK,
)
async def get_card_cashback(
    card_number: str,
    bank_name: str,
    month: date,
    db: AsyncSession = Depends(get_session)
):
    cashbacks = await user_cashback_crud.card_cashbacks(
        db=db,
        card_number=card_number,
        month=month
    )
    
    return schemas.CardWithCashbacks(
        bank=bank_name,
        card_number=card_number,
        month=month,
        cashbacks=[
            schemas.CardCashback(
                product_type=cashback.cashback.product_type,
                value=cashback.value
            )
            for cashback in cashbacks
        ]
    )


@router.post(
    '/get_card_cashback_and_transactions/',
    status_code=status.HTTP_200_OK,
)
async def get_card_cashback_and_transactions(
    card_number: str,
    bank_name: str,
    month: date,
    db: AsyncSession = Depends(get_session)
) -> schemas.CardWithCashbacksandTransactions:
    cashbacks = await user_cashback_crud.card_cashbacks(
        db=db,
        card_number=card_number,
        month=month
    )

    transactions: List[models.Transaction] = await transaction_crud.get_card_transactions(
        db=db,
        card_number=card_number,
        month=month
    )

    return schemas.CardWithCashbacksandTransactions(
        bank=bank_name,
        card_number=card_number,
        month=month,
        cashbacks=[
            schemas.CardCashback(
                product_type=cashback.cashback.product_type,
                value=cashback.value
            )
            for cashback in cashbacks
        ],
        transactions=[
            schemas.Transaction.from_orm(transaction)
            for transaction in transactions
        ]
    )