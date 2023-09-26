import os
from typing import List
from collections import Counter

from schemas import base as schemas
from models import base as models

import nltk
from nltk.corpus import stopwords
from string import punctuation
import spacy
from langdetect import detect

from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.models import load_model

import tensorflow_addons as tfa
import tensorflow as tf

from services.banks import get_categories_values, get_card_transactions

nltk.download('stopwords')

nlp_eng = spacy.load('en_core_web_sm', disable=['ner', 'parser'])
nlp_rus = spacy.load('ru_core_news_sm', disable=['ner', 'parser'])

stop_words_rus = stopwords.words('russian')
stop_words_eng = stopwords.words('english')
stop_words = stop_words_rus+stop_words_eng+['каждый день', 'каждый', 'день', 'красная цена', 'красная', 'цена', 'верный', 'дикси', 'моя', 'моя цена', 'окей','то, что надо!', 'smart','spar', 'ашан']


def preprocess_sentences(sentences, tokenizer, max_length):
    with open('new_tokenizer_LSTM.pkl', 'rb') as f:
        tokenizer = pickle.load(f)
        
    sequences = tokenizer.texts_to_sequences(sentences)
    padded_sequences = pad_sequences(sequences, maxlen=max_length, padding='post', truncating='post')
    return padded_sequences
    

def get_n_most_frequent_strings(strings: List[str], n: int = 3) -> List[str]:
    string_counts = Counter(strings)

    most_common_strings = string_counts.most_common(n)
    result = [string for string, count in most_common_strings]

    return result


class Cashbacker:
    def __init__(self, card:models.Card):
        self.card = card
    
     def tokenize_text(products):

        all_sentence = []

        for value in products:
            lang = detect(value)

            if lang == 'en':
                doc = nlp_eng(value)
                lemmas = [token.lemma_ for token in doc if token.is_alpha and token.text not in punctuation and token.text.lower() not in stop_words]
                cleaned_sentence = " ".join(lemmas)
                all_sentence.append(cleaned_sentence)
            else:
                doc = nlp_rus(value)
                lemmas = [token.lemma_ for token in doc if token.is_alpha and token.text not in punctuation and token.text.lower() not in stop_words]
                cleaned_sentence = " ".join(lemmas)
                all_sentence.append(cleaned_sentence)

        padded_sequences = preprocess_sentences(all_sentence, tokenizer, 29)

        return padded_sequences


    def get_topics_name(self, product_names):
        tokens = tokenize_text(product_names)
        model = load_model("new_model_LSTM.h5", custom_objects={'Addons>F1Score': tfa.metrics.F1Score})
        tf.config.run_functions_eagerly(True)
        predictions = np.argmax(loaded_model.predict(tokens), axis=1)
        dictionary =  { "topic": ['автозапчасти', 'видеоигры', 'напитки', 'продукты питания', 'закуски и приправы', 'аквариум', 'одежда', 'уборка', 'электроника', 'образование'], 
                       "label": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9] }
        topics=[]
        for index in range(len(predictions)):
          label = predictions[index].item()
          topic = dictionary['topic'][dictionary['label'].index(label)]
          topics.append(topic)
        return topics

        
    def calculate_cashback_categories(self) -> List[schemas.Cashback]:
        card = self.card
        transactions = get_card_transactions(card)

        categories = self.get_topics_name([transaction['product_name'] for transaction in transactions])
        best_categories = get_n_most_frequent_strings(categories, n=5)
        best_categories_values = get_categories_values(card.bank, best_categories)

        cashback_list = []
        for current_category in best_categories_values:
            cashback_list.append(schemas.Cashback(product_type=current_category[0], value=current_category[1]))

        return cashback_list
