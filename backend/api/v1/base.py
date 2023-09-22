from datetime import date, timedelta
from typing import Annotated, List
from fastapi import APIRouter, Depends, status, HTTPException, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from services.validation import validate_photo

from exceptions.auth import AuthError
from services.auth import ACCESS_TOKEN_EXPIRE_DAYS, authenticate_user, create_access_token, get_cards, get_current_user, get_user_by_photo
from services.db import card_crud, user_cashback_crud, cashback_crud, user_crud
from services.cashback import can_choose_cashback, create_cards_and_cashbacks, get_card_cashback, get_card_choose_cashback
from db.db import get_session
from schemas import base as schemas
from models import base as models


router = APIRouter()


@router.post(
    '/terminal',
    status_code=status.HTTP_200_OK,
    response_model=schemas.TerminalResponse
)
async def terminal(
    file_in: UploadFile,
    db: AsyncSession = Depends(get_session)
) -> schemas.TerminalResponse:
    photo_validation = validate_photo(file_in)
    if not photo_validation:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    user_info: schemas.GosuslugiUser = get_user_by_photo(file_in)
    if user_info:
        cards: List[schemas.LiteCard] = get_cards(user_info.gosuslugi_id)

        user: models.User | None = await user_crud.get(
            db, user_info.gosuslugi_id
        )

        if not user:
            return schemas.TerminalResponse(
                name=user_info.first_name,
                surname=user_info.surname,
                cards=[
                    schemas.CardWithCashback(
                        bank=card.bank,
                        last_four_digits=card.card_number[-4:],
                        cashback=[]
                    ) for card in cards
                ]
            )
        
        today = date.today()
        month = date(year=today.year, month=today.month, day=1)

        await create_cards_and_cashbacks(db, cards, user, month)

        cards_in_db = await card_crud.get_card_with_month_cashback(
            db=db,
            user_id=user.id,
            month=month
        )

        cards_with_cahback = [
            schemas.CardWithCashback(
                bank=card.bank,
                last_four_digits=card.last_four_digits,
                cashback=card.cashback
            ) for card in cards_in_db
        ]
        return schemas.TerminalResponse(
            name=user_info.first_name,
            surname=user_info.surname,
            cards=cards_with_cahback
        )


@router.post('/auth', response_model=schemas.Token)
async def get_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_session)
) -> schemas.Token:
    user_info: schemas.GosuslugiUser | None = await authenticate_user(
        db, form_data.username, form_data.password
    )

    if not user_info:
        raise AuthError
    
    user: models.User = await user_crud.get_or_create(db, user_info)

    cards: List[schemas.LiteCard]= get_cards(user.gosuslugi_id)

    today = date.today()
    month = date(year=today.year, month=today.month, day=1)

    await create_cards_and_cashbacks(db, cards, user, month)

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

    today = date.today()
    month = date(year=today.year, month=today.month, day=1)

    cards = await card_crud.get_card_with_month_cashback(
        db=db,
        user_id=user.id,
        month=month
    )
    return cards


@router.get(
    '/get_cashback_for_choose/{card_id}',
    status_code=status.HTTP_202_ACCEPTED,
    response_model=schemas.FullCardWithCashback,
    description='Получение списка доступных кешбеков по карте'
)
async def get_cashback_for_choose(
    card_id,
    current_user: Annotated[schemas.FullUser, Depends(get_current_user)],
    db: AsyncSession = Depends(get_session),
) -> schemas.FullCardWithCashback:
    """
        в заголовке запроса  необходимо указать токен:
        - Authorization: Bearer <token>
    """
    card: models.Card | None = await card_crud.get(db, id=int(card_id))
    today = date.today()
    month = date(year=today.year, month=today.month, day=1)
    if card:
        month_cashbacks = await user_cashback_crud.filter_by(
            db=db,
            card_id=card.id,
            month=month,
            status=True
        )
        cashback_already_choosen: bool = False
        for month in month_cashbacks:
            cashback_already_choosen = True
    if (
        card
        and card.user_id == current_user.id
        and can_choose_cashback(card)
        and not cashback_already_choosen
    ):

        cashbacks = get_card_choose_cashback(card)
        for cashback in cashbacks:
            # код в цикле повторяется в другом эндпоинте, можно вынести в функцию
            cashback_in_db: models.Cashback = await cashback_crud.get_or_create(
                db=db,
                obj_in=cashback
            )
            # создавать кешбек конкретного пользователя
            await user_cashback_crud.get_or_create(
                db=db,
                obj_in=schemas.UserCashback(
                    card_id=card.id,
                    cashback_id=cashback_in_db.id,
                    month=month,
                    status=False
                )
            )
        
        return schemas.FullCardWithCashback(
            card_id=int(card_id),
            bank=card.bank,
            last_four_digits=card.card_number[-4:],
            cashback=cashbacks,
            can_choose=can_choose_cashback(card)
        )
    
    raise HTTPException


@router.post(
    '/choose_card_cashback/{card_id}',
    status_code=status.HTTP_200_OK,
    description='Установка кешбеков на месяц',
    response_model=List[schemas.Cashback]
)
async def choose_card_cashback(
    card_id,
    month_cashback: schemas.MonthCashback,
    current_user: Annotated[schemas.FullUser, Depends(get_current_user)],
    db: AsyncSession = Depends(get_session),
):
    card: models.Card | None = await card_crud.get(db, id=int(card_id))

    if card and card.user_id == current_user.id:
        month: date = month_cashback.month
        month = date(year=month.year, month=month.month, day=1)

        try:
            cashbacks = [
                await cashback_crud.get(
                    db, product_type=cashback.product_type, value=cashback.value
                ) for cashback in month_cashback.cashback
            ]

            user_cashbacks = [
                await user_cashback_crud.get(
                    db,
                    obj_in=schemas.UserCashback(
                        card_id=card.id,
                        cashback_id=cashback.id,
                        month=month,
                        status=False
                    )
                ) for cashback in cashbacks
            ]

            choosen_user_cashbacks = [
                await user_cashback_crud.update(
                    db,
                    obj_in=schemas.UserCashback(
                        card_id=card.id,
                        cashback_id=cashback.cashback_id,
                        month=month,
                        status=False
                    ),
                    status=True
                ) for cashback in user_cashbacks
            ]
        except:
            raise HTTPException
        
        return month_cashback.cashback

    raise HTTPException

