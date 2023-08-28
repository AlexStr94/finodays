from typing import List

from models import base as models
from schemas import base as schemas

from cashbacker.casbacker import Cashbacker

cashbacker = Cashbacker()


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
        # return [
        #     schemas.Cashback(
        #         product_type='Напитки',
        #         value=5
        #     ),
        #     schemas.Cashback(
        #         product_type='Продукты питания',
        #         value=5
        #     ),
        #     schemas.Cashback(
        #         product_type='Садоводство',
        #         value=3
        #     ),
        #     schemas.Cashback(
        #         product_type='Одежда',
        #         value=5
        #     ),
        #     schemas.Cashback(
        #         product_type='Видеоигры',
        #         value=5
        #     )
        # ]

        return cashbacker.calculate_cashback_categories(card)

    return None
