from datetime import date, timedelta
from dateutil import relativedelta
from random import randint
from typing import Annotated, List
from fastapi import APIRouter, Depends, status, HTTPException, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from services.validation import validate_photo

from exceptions.auth import AuthError
from services.auth import ACCESS_TOKEN_EXPIRE_DAYS, create_access_token, get_current_user, get_user_by_photo
from services.db import account_crud, user_cashback_crud, cashback_crud, user_crud, transaction_crud
from services.external_integrations import authenticate_user, create_or_update_accounts_in_db, get_account_cashbacks, get_accounts, update_user_transactions
from services.cashback import can_choose_cashback, get_card_choose_cashback
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
    # чуть позже переделаю
    # user_info: schemas.User = get_user_by_photo(file_in)
    user_info: schemas.User | None = await authenticate_user(
        'username', 'password'
    )
    if user_info:

        accounts: List[schemas.RawAccount] | None = get_accounts(user_info.gosuslugi_id)
        
        if accounts:
            cards = []
            today = date.today()
            month = date(year=today.year, month=today.month, day=1)

            for account in accounts:
                account_cashbacks = get_account_cashbacks(
                    account_number=account.number,
                    month=month
                )
                cashbacks: List[schemas.RawAccountCashbacks]
                if account_cashbacks:
                    cashbacks = account_cashbacks.cashbacks

                account_card = [
                    schemas.CardWithCashback(
                        bank=account.bank,
                        last_four_digits=card.card_number[-4:],
                        cashbacks=cashbacks
                    )
                    for card in account.cards
                ]

                cards += account_card

            return schemas.TerminalResponse(
                name=user_info.first_name,
                surname=user_info.surname,
                cards=cards
            )
        
    raise HTTPException(404)
   


@router.post('/auth', response_model=schemas.Token)
async def get_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_session)
) -> schemas.Token:
    user_info: schemas.User | None = await authenticate_user(
        form_data.username, form_data.password
    )

    if not user_info:
        raise AuthError
    
    user: models.User = await user_crud.get_or_create(db, user_info)

    accounts: List[schemas.RawAccount] | None = get_accounts(user.gosuslugi_id)

    if accounts:
        today = date.today()
        month = date(year=today.year, month=today.month, day=1)

        await create_or_update_accounts_in_db(db, accounts, user, month)

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
    description='Получение списка карт пользователя с кешбеком',
    response_model=List[schemas.AccountWithCardsAndCashbacks]
)
async def get_cards_list(
    current_user: Annotated[schemas.FullUser, Depends(get_current_user)],
    db: AsyncSession = Depends(get_session),
) -> List[schemas.AccountWithCardsAndCashbacks]:
    """
        в заголовке запроса  необходимо указать токен:
        - Authorization: Bearer <token>
    """
    today = date.today()
    month = date(year=today.year, month=today.month, day=1)

    result = await account_crud.get_user_accounts(
        db=db,
        user_id=current_user.id,
        month=month
    )
    
    return result


@router.get(
    '/get_cashback_for_choose/',
    status_code=status.HTTP_202_ACCEPTED,
    response_model=schemas.CashbacksForChoose,
    description='Получение списка доступных кешбеков по карте'
)
async def get_cashback_for_choose(
    account_number,
    current_user: Annotated[schemas.FullUser, Depends(get_current_user)],
    db: AsyncSession = Depends(get_session),
) -> schemas.CashbacksForChoose:
    """
        в заголовке запроса  необходимо указать токен:
        - Authorization: Bearer <token>
    """
    account: models.Account | None = await account_crud.get(
        db, number=account_number
    )
    today = date.today()
    month = date(year=today.year, month=today.month, day=1)
    if account:
        # проверяем, есть ли кэшбеки на месяц для этого пользователя
        month_cashbacks = await user_cashback_crud.filter_by(
            db=db,
            account_id=account.id,
            month=month,
            status=True
        )
    if (
        account
        and account.user_id == current_user.id
        and can_choose_cashback(account)
        and not month_cashbacks
    ):  
        # если уже формировали кэшбеки, их и возвращаем, чтобы
        # не было дублей
        not_accepted_cashbacks = await user_cashback_crud.filter_by(
            db=db,
            with_cashbacks=True,
            account_id=account.id,
            month=month,
            status=False
        )

        if not_accepted_cashbacks:
            return schemas.CashbacksForChoose(
                account_number=account.number,
                bank=account.bank,
                cashbacks=[
                    schemas.Cashback(
                        product_type=user_cashback.cashback.product_type,
                        value=user_cashback.value
                    )
                    for user_cashback in not_accepted_cashbacks
                ],
                can_choose_cashback=can_choose_cashback(account)
            )

        # Если еще не формировали кэшбеки, то формируем
        raw_cashbacks = get_card_choose_cashback(account)
        cashbacks: List[schemas.Cashback] = []
        for cashback in raw_cashbacks:
            cashback_in_db: models.Cashback = await cashback_crud.get_or_create(
                db=db,
                obj_in=schemas.CashbackCreate.create_from_raw_cashback(cashback)
            )
            # создавать кешбек конкретного пользователя
            user_cashback = await user_cashback_crud.get_or_create(
                db=db,
                obj_in=schemas.UserCashbackCreate(
                    account_id=account.id,
                    cashback_id=cashback_in_db.id,
                    month=month,
                    status=False,
                    value=randint(3, 10) #может как-то умнее предлагать?
                )
            )
            cashbacks.append(
                schemas.Cashback(
                    product_type=cashback_in_db.product_type,
                    value=user_cashback.value
                )
            )
        
        return schemas.CashbacksForChoose(
            account_number=account.number,
            bank=account.bank,
            cashbacks=cashbacks,
            can_choose_cashback=can_choose_cashback(account)
        )
    
    raise HTTPException(status_code=404, detail="Resource not found")


@router.post(
    '/choose_card_cashback/',
    status_code=status.HTTP_200_OK,
    description='Установка кешбеков на месяц',
    response_model=List[schemas.Cashback]
)
async def choose_card_cashback(
    month_cashback: schemas.MonthCashback,
    current_user: Annotated[schemas.FullUser, Depends(get_current_user)],
    db: AsyncSession = Depends(get_session),
):
    account: models.Account | None = await account_crud.get(
        db, number=month_cashback.account_number
    )

    if account and account.user_id == current_user.id:
        month: date = month_cashback.month
        month = date(year=month.year, month=month.month, day=1)

        try:
            cashbacks: List[models.Cashback] = await cashback_crud.bulk_get(
                db=db, cashbacks=month_cashback.cashback
            )

            cashbacks_data = zip(month_cashback.cashback, cashbacks)
            # слабое место
            user_cashbacks = [
                await user_cashback_crud.get(
                    db,
                    account_id=account.id,
                    cashback_id=cashback_data[1].id,
                    month=month,
                    status=False,
                    value=cashback_data[0].value
                ) for cashback_data in cashbacks_data
            ]

            choosen_user_cashbacks = [
                await user_cashback_crud.update(
                    db,
                    obj_in=schemas.UserCashbackUpdate(
                        id=user_cashback.id,
                        status=True
                    )
                ) for user_cashback in user_cashbacks
            ]
        except:
            raise HTTPException
        
        return month_cashback.cashback

    raise HTTPException


@router.get(
    '/transactions/',
    status_code=status.HTTP_200_OK,
    description='Получение списка карт пользователя с кешбеком',
    response_model=List[schemas.AccountWithTransactions]
)
async def get_transactions(
    current_user: Annotated[schemas.FullUser, Depends(get_current_user)],
    db: AsyncSession = Depends(get_session),
) -> List[schemas.AccountWithTransactions]:
    await update_user_transactions(
        db=db,
        user_id=current_user.id
    )

    today = date.today()
    month = date(year=today.year, month=today.month, day=1)

    return await account_crud.get_user_accounts_with_transactions(
        db=db, user_id=current_user.id, month=month
    )
