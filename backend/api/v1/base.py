from datetime import date, timedelta
from typing import Annotated, List
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from exceptions.auth import AuthError
from services.auth import ACCESS_TOKEN_EXPIRE_DAYS, authenticate_user, create_access_token, get_cards, get_current_user
from services.db import card_crud, user_cashback_crud, cashback_crud, user_crud
from services.cashback import get_card_cashback
from db.db import get_session
from schemas import base as schemas
from models import base as models


router = APIRouter()


@router.post('/auth', response_model=schemas.Token)
async def get_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_session)
) -> schemas.Token:
    user_info: schemas.GosuslugiUser | None = authenticate_user(
        form_data.username, form_data.password
    )

    if not user_info:
        raise AuthError
    
    user: models.User = await user_crud.get_or_create(db, user_info)

    cards: List[schemas.LiteCard]= get_cards(user.gosuslugi_id)

    for card in cards:
        card_in_db: models.Card = await card_crud.get_or_create(
            db=db,
            obj_in=schemas.Card(
                user_id=user.id,
                bank=card.bank,
                card_number=card.card_number
            )
        )

        # получаем от банка уже выбранные кешбеки
        cashbacks: List[schemas.Cashback] | None = get_card_cashback(card_in_db)
        # тут есть над чем подумать. Если выбран и на следующий месяц кешбек?
        _date = date.today()

        if cashbacks:
            for cashback in cashbacks:
                cashback_id_db: models.Cashback = await cashback_crud.get_or_create(
                    db=db,
                    obj_in=cashback
                )

                # создавать кешбек конкретного пользователя

                await user_cashback_crud.get_or_create(
                    db=db,
                    obj_in=schemas.UserCashback(
                        card_id=card_in_db.id,
                        cashback_id=cashback_id_db.id,
                        month=_date,
                        status=True
                    )
                )

    access_token_expires = timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    access_token = create_access_token(
        data={"sub": user.gosuslugi_id}, expires_delta=access_token_expires
    )
    return schemas.Token(
        access_token=access_token,
        token_type='bearer'
    )


@router.get(
    '/cards',
    status_code=status.HTTP_200_OK,
    description='Получение списка карт пользователя с кешбеком'
)
async def get_cards_list(
    current_user: Annotated[schemas.FullUser, Depends(get_current_user)],
    db: AsyncSession = Depends(get_session),
):
    """
        в заголовке запроса  необходимо указать токен:
        - Authorization: Bearer <token>
    """
    user: models.User = await user_crud.get(db, current_user.gosuslugi_id)

    cards = await card_crud.get_multi(db, user_id=user.id)
    return cards