from datetime import date, timedelta
from typing import Annotated, List

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.security import OAuth2PasswordRequestForm

from cashbacker.casbacker import categorizer
from db.db import get_session
from exceptions import auth as auth_exceptions
from exceptions import api as api_exceptions
from models import base as models
from schemas import base as schemas
from services.auth import (ACCESS_TOKEN_EXPIRE_DAYS, create_access_token,
                           get_current_user)
from services.cashback import can_choose_cashback, get_card_choose_cashback
from services.db import (account_crud, category_limit_crud, cashback_crud,
                         user_cashback_crud, user_crud)
from services.external_integrations import (authenticate_user,
                                            create_or_update_accounts_in_db,
                                            get_account_cashbacks,
                                            get_accounts, get_user_by_photo,
                                            update_user_transactions)
from services.gigachat import financial_analyst
from services.validation import validate_photo


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
    photo: bytes = await file_in.read()
    # await asyncio.to_thread(validate_photo, image=photo)
    photo_validation = True
    if not photo_validation:
        raise auth_exceptions.AntiSpoofingException()

    user_info: schemas.User = await get_user_by_photo(photo, file_in.filename)

    if user_info:

        accounts: List[schemas.RawAccount] | None = await get_accounts(
            user_info.gosuslugi_id)

        if accounts:
            cards = []
            today = date.today()
            month = date(year=today.year, month=today.month, day=1)

            for account in accounts:
                # Условие ниже нужно только для демонстрации на
                # стенде. В боевом варианте должно отрабатывать только
                # выражение в else
                if account.bank == 'Центр-инвест':
                    account_cashbacks = schemas.RawAccountCashbacks(
                        month=month,
                        cashbacks=[
                            schemas.RawCashback(
                                product_type='продукты питания',
                                value=5
                            ),
                            schemas.RawCashback(
                                product_type='одежда',
                                value=7
                            ),
                            schemas.RawCashback(
                                product_type='электроника',
                                value=3
                            )
                        ]

                    )
                else:
                    account_cashbacks = await get_account_cashbacks(
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

    raise auth_exceptions.EBSExceptin()


@router.post('/auth', response_model=schemas.Token)
async def get_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_session)
) -> schemas.Token:
    user_info: schemas.User | None = await authenticate_user(
        form_data.username, form_data.password
    )

    if not user_info:
        raise auth_exceptions.AuthError()

    user: models.User = await user_crud.get_or_create(db, user_info)

    user_id: int = user.id

    accounts: List[schemas.RawAccount] | None = await get_accounts(user_info.gosuslugi_id)

    if accounts:
        today = date.today()
        month = date(year=today.year, month=today.month, day=1)

        await create_or_update_accounts_in_db(db, accounts, user_id, month)

    access_token_expires = timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    access_token = create_access_token(
        data={"sub": user_info.gosuslugi_id}, expires_delta=access_token_expires
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
        account_id: int = account.id
        account_bank = account.bank
        account_user_id = account.user_id
        # проверяем, есть ли кэшбеки на месяц для этого пользователя
        month_cashbacks = await user_cashback_crud.filter_by(
            db=db,
            account_id=account_id,
            month=month,
            status=True
        )
    else:
        raise api_exceptions.AccountNotFoundException()
    if (
        account
        and account_user_id == current_user.id
        and can_choose_cashback(account_bank)
        and not month_cashbacks
    ):
        # если уже формировали кэшбеки, их и возвращаем, чтобы
        # не было дублей
        not_accepted_cashbacks = await user_cashback_crud.filter_by(
            db=db,
            with_cashbacks=True,
            account_id=account_id,
            month=month,
            status=False
        )

        if not_accepted_cashbacks:
            return schemas.CashbacksForChoose(
                account_number=account_number,
                bank=account_bank,
                cashbacks=[
                    schemas.Cashback(
                        product_type=user_cashback.cashback.product_type,
                        value=user_cashback.value
                    )
                    for user_cashback in not_accepted_cashbacks
                ],
                can_choose_cashback=can_choose_cashback(account_bank)
            )

        # Если еще не формировали кэшбеки, то формируем
        raw_cashbacks = await get_card_choose_cashback(
            db=db, account=account, month=month
        )
        cashbacks: List[schemas.Cashback] = []
        for cashback in raw_cashbacks:
            cashback_in_db: models.Cashback = await cashback_crud.get_or_create(
                db=db,
                obj_in=schemas.CashbackCreate.create_from_raw_cashback(
                    cashback)
            )
            cashback_in_db_id = cashback_in_db.id
            cashback_in_db_product_type = cashback_in_db.product_type

            # создавать кешбек конкретного пользователя
            await user_cashback_crud.get_or_create(
                db=db,
                obj_in=schemas.UserCashbackCreate(
                    account_id=account_id,
                    cashback_id=cashback_in_db_id,
                    month=month,
                    status=False,
                    value=cashback.value
                )
            )
            cashbacks.append(
                schemas.Cashback(
                    product_type=cashback_in_db_product_type,
                    value=cashback.value
                )
            )

        return schemas.CashbacksForChoose(
            account_number=account_number,
            bank=account_bank,
            cashbacks=cashbacks,
            can_choose_cashback=can_choose_cashback(account_bank)
        )
    else:
        raise api_exceptions.CashbackAlreadyChoosenException()


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
            # При получении сортируем по product_type, т.к.
            # ответ может приходить в другом порядке
            cashbacks: List[models.Cashback] = await cashback_crud.bulk_get(
                db=db, cashbacks=month_cashback.cashback
            )

            month_cashbacks = list(
                sorted(month_cashback.cashback, key=lambda x: x.product_type))
            cashbacks_data = zip(month_cashbacks, cashbacks)
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
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

        return month_cashback.cashback

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)


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


@router.post(
    '/get_category/',
    description='Определение категории кэшбека для транзакции',
    status_code=status.HTTP_200_OK,
    response_model=schemas.CategoryName
)
async def get_category(transaction: schemas.TransactionName):
    category_lst = await categorizer.get_topics_name([transaction.name])
    return schemas.CategoryName(
        name=category_lst[0]
    )


@router.get(
    '/gigi_chat/',
    status_code=status.HTTP_200_OK,
    response_model=schemas.GigaChatAnswer
)
async def gigi_chat(
    promt: int,
    current_user: Annotated[schemas.FullUser, Depends(get_current_user)],
    db: AsyncSession = Depends(get_session),
):
    if promt == 1:
        answer = await financial_analyst.limit_analysis(
            db=db, user_id=current_user.id
        )
        if not answer:
            answer = 'Вы не установили лимиты'
    elif promt == 2:
        answer = await financial_analyst.spendings_analysis(
            db=db, user_id=current_user.id
        )
        if not answer:
            answer = 'У вас не было трат в этом месяце'

    return schemas.GigaChatAnswer(
        answer=answer
    )


@router.post(
    '/set_limit/',
    status_code=status.HTTP_200_OK,
    response_model=schemas.Limit
)
async def set_limit(
    raw_limit: schemas.RawLimit,
    current_user: Annotated[schemas.FullUser, Depends(get_current_user)],
    db: AsyncSession = Depends(get_session)
):
    limit = await category_limit_crud.create_or_update(
        db=db, obj_in=schemas.CreateLimit.create_from_raw_limit(
            raw_limit=raw_limit, user_id=current_user.id
        )
    )

    return schemas.Limit.from_orm(limit)


@router.get(
    '/limits/',
    status_code=status.HTTP_200_OK,
    response_model=List[schemas.RawLimit]
)
async def limits(
    current_user: Annotated[schemas.FullUser, Depends(get_current_user)],
    db: AsyncSession = Depends(get_session)
):
    limits = await category_limit_crud.filter_by(
        db=db, user_id=current_user.id
    )
    return [
        schemas.Limit.from_orm(limit)
        for limit in limits
    ]


@router.get(
    '/log_out/',
    status_code=status.HTTP_200_OK
)
async def log_out(
    current_user: Annotated[schemas.FullUser, Depends(get_current_user)],
    db: AsyncSession = Depends(get_session),
):
    """
        Для демонстрации на стенде, при выходе из приложения
        удаляет выбранные кэшбеки для счетов Центр-инвеста
    """
    centr_invest_accounts: List[models.Account] = await account_crud.filter_by(
        db=db, bank='Центр-инвест', user_id=current_user.id
    )

    for account in centr_invest_accounts:
        user_cashbacks: List[models.UserCashback] = await user_cashback_crud.filter_by(
            db=db, account_id=account.id
        )
        for user_cashback in user_cashbacks:
            await user_cashback_crud.delete(
                db=db, obj=user_cashback
            )

    return {'message': 'ok'}
