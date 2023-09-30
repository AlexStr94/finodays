from typing import List

from cashbacker.fake_transactions import get_fake_transactions
from models import base as models


def get_card_transactions(card: models.Card):
    return get_fake_transactions()


def get_categories_values(bank: str, categories: List[str]) -> List[str | int]:
    values = []

    for current_category in categories:
        values.append((current_category, 5))

    return values
