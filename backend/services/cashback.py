from datetime import date
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from models import base as models
from schemas import base as schemas

from cashbacker.casbacker import Cashbacker


def get_card_cashback(card: models.Card) -> List[schemas.Cashback] | None:
    if card.bank == 'Тинькофф':
        return [
            schemas.Cashback(
                product_type='Продукты питания',
                value=5
            ),
            schemas.Cashback(
                product_type='Садоводство',
                value=3
            ),
            schemas.Cashback(
                product_type='Одежда',
                value=5
            )
        ]

    return None


def can_choose_cashback(card: models.Card) -> bool:
    if card.bank == 'Центр-инвест':
        return True

    return False


def get_card_choose_cashback(card: models.Card) -> List[schemas.Cashback] | None:
    if can_choose_cashback(card):
        return Cashbacker(card).calculate_cashback_categories()

    return None

async def create_cards_and_cashbacks(
    db: AsyncSession,
    cards: List[schemas.LiteCard],
    user: models.User,
    month: date
) -> None:
    from services.db import card_crud, cashback_crud, user_cashback_crud
    
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
                        month=month,
                        status=True
                    )
                )