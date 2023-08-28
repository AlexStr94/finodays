from typing import List
from collections import Counter

from schemas import base as schemas
from models import base as models

from services.banks import get_categories_values, get_card_transactions


def get_n_most_frequent_strings(strings: List[str], n: int = 3) -> List[str]:
    string_counts = Counter(strings)

    most_common_strings = string_counts.most_common(n)
    result = [string for string, count in most_common_strings]

    return result


class Cashbacker:
    def __int__(self):
        ...
        # тут сохранить инстансы моделей, чтобы не инициализировать кажндый раз

    @staticmethod
    def __get_product_categories(self, products_names: List[str]) -> List[str]:
        # тут должна быть обработка названий и возврат типов
        # пока заглушка
        return [
            'продукты питания',
            'напитки',
            'электроника',
            'продукты питания',
            'напитки',
            'электроника',
            'продукты питания',
            'напитки',
            'электроника',
            'продукты питания',
            'напитки',
            'электроника',
        ]

    @staticmethod
    def calculate_cashback_categories(self, card: models.Card) -> List[schemas.Cashback]:
        transactions = get_card_transactions(card)

        categories = self.__get_product_categories([transaction['product_name'] for transaction in transactions])
        best_categories = get_n_most_frequent_strings(categories)
        best_categories_values = get_categories_values(card.bank, best_categories)

        cashback_list = []
        for current_category in best_categories_values:
            cashback_list.append(schemas.Cashback(product_type=current_category[0], value=current_category[1]))

        return cashback_list
