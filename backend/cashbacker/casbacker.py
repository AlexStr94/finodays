from typing import List
from collections import Counter
from core.config import app_settings

from schemas import base as schemas
from models import base as models

import nltk
from sklearn.feature_extraction.text import CountVectorizer
from nltk.corpus import stopwords
from string import punctuation
import spacy
from langdetect import detect

import openai

from services.banks import get_categories_values, get_card_transactions

openai.api_key = app_settings.gpt_key

nltk.download('stopwords')

nlp_eng = spacy.load('en_core_web_sm', disable=['ner', 'parser'])
nlp_rus = spacy.load('ru_core_news_sm', disable=['ner', 'parser'])

stop_words_rus = stopwords.words('russian')
stop_words_eng = stopwords.words('english')
stop_words = stop_words_rus+stop_words_eng+['каждый день', 'каждый', 'день', 'красная цена', 'красная', 'цена', 'верный', 'дикси', 'моя', 'моя цена', 'окей','то, что надо!', 'smart','spar', 'ашан']


def get_n_most_frequent_strings(strings: List[str], n: int = 3) -> List[str]:
    string_counts = Counter(strings)

    most_common_strings = string_counts.most_common(n)
    result = [string for string, count in most_common_strings]

    return result


class Cashbacker:
    def __init__(self, card:models.Card):
        self.card = card

    def __get_product_categories(self, products_names: List[str]) -> List[str]:

        return self.topic_list(products_names)

    
    def topic_list(self, products):

        topics = []
    
        for value in products:
            try:
                lang = detect(value)

                if lang == 'en':
                    doc = nlp_eng(value)
                    topic = self.topic_naming(doc)
                    topics.append(topic)
                else:
                    doc = nlp_rus(value)
                    topic = self.topic_naming(doc)
                    topics.append(topic)
            except Exception as e:
                print(f"Error processing value: {value}")
                print(f"Error message: {str(e)}")

        return topics

    
    def topic_naming(self,doc):
         
        items = ['автозапчасти', 'видеоигры', 'напитки', 'продукты питания', 'закуски и приправы', 'аквариум', 'одежда', 'уборка', 'образование', 'электроника']
        system = f'{items} из перечисленных категорий, ТОЧНО выбери одну и укажи ТОЛЬКО её (без знаков препинания и дополнительных слов). Новых предлагать нельзя Регистр должен быть тем же. Только из списка'
        
        lemmas = [token.lemma_ for token in doc if token.is_alpha and token.text not in punctuation]
        vectorizer = CountVectorizer(stop_words=stop_words)
        x = vectorizer.fit_transform(lemmas)
        tokens = vectorizer.get_feature_names_out()
        content = f'{items} выбери категорию на основе списка слов ниже: {" ".join(tokens)}'
        
        completion = openai.ChatCompletion.create(
          model="gpt-3.5-turbo",
          messages=[{"role": "system", "content": system},
            {"role": "user", "content": content}], max_tokens= 20, temperature=0.05)
        response_content = completion["choices"][0]["message"]["content"]
        
        return response_content
        
    def calculate_cashback_categories(self) -> List[schemas.Cashback]:
        card = self.card
        transactions = get_card_transactions(card)

        categories = self.__get_product_categories([transaction['product_name'] for transaction in transactions])
        best_categories = get_n_most_frequent_strings(categories, n=5)
        best_categories_values = get_categories_values(card.bank, best_categories)

        cashback_list = []
        for current_category in best_categories_values:
            cashback_list.append(schemas.Cashback(product_type=current_category[0], value=current_category[1]))

        return cashback_list
