import os
from typing import List
from collections import Counter

import pandas as pd
import numpy as np

import nltk
from nltk.corpus import stopwords
from string import punctuation
import spacy
from langdetect import detect

from keras.preprocessing.sequence import pad_sequences
from keras.models import load_model
import pickle

import tensorflow_addons as tfa
import tensorflow as tf

from sklearn.preprocessing import StandardScaler


nltk.download('stopwords')

nlp_eng = spacy.load('en_core_web_sm', disable=['ner', 'parser'])
nlp_rus = spacy.load('ru_core_news_sm', disable=['ner', 'parser'])

stop_words_rus = stopwords.words('russian')
stop_words_eng = stopwords.words('english')
stop_words = stop_words_rus + stop_words_eng + ['каждый день',
                                                'каждый', 'день', 'красная цена', 'красная', 'цена',
                                                'верный', 'дикси', 'моя', 'моя цена', 'окей', 'то, что надо!',
                                                'smart', 'spar', 'ашан']

best_look_back = 22


def get_n_most_frequent_strings(strings: List[str], n: int = 3) -> List[str]:
    string_counts = Counter(strings)

    most_common_strings = string_counts.most_common(n)
    result = [string for string, _ in most_common_strings]

    return result


class Categorizer:
    def __init__(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        model_path = os.path.join(current_dir, 'LSTM_model.h5')
        tokenizer_path = os.path.join(current_dir, 'LSTM_tokenizer.pkl')
        
        self.topic_model = load_model(model_path,
                                      custom_objects={'Addons>F1Score': tfa.metrics.F1Score})
        with open(tokenizer_path, 'rb') as f:
            self.tokenizer = pickle.load(f)

    def preprocess_sentences(self, sentences, max_length):
        sequences = self.tokenizer.texts_to_sequences(sentences)
        padded_sequences = pad_sequences(sequences, maxlen=max_length, padding='post', truncating='post')
        return padded_sequences

    def tokenize_text(self, products):

        all_sentence = []

        for value in products:
            lang = detect(value)

            if lang == 'en':
                doc = nlp_eng(value)
                lemmas = [token.lemma_ for token in doc if token.is_alpha
                          and token.text not in punctuation and token.text.lower() not in stop_words]
                cleaned_sentence = " ".join(lemmas)
                all_sentence.append(cleaned_sentence)
            else:
                doc = nlp_rus(value)
                lemmas = [token.lemma_ for token in doc if token.is_alpha
                          and token.text not in punctuation and token.text.lower() not in stop_words]
                cleaned_sentence = " ".join(lemmas)
                all_sentence.append(cleaned_sentence)

        padded_sequences = self.preprocess_sentences(all_sentence, 40)

        return padded_sequences

    def get_topics_name(self, product_names: list) -> list:
        tokens = self.tokenize_text(product_names)
        model = self.topic_model
        tf.config.run_functions_eagerly(True)
        predictions = np.argmax(model.predict(tokens), axis=1)
        dictionary = {
            "topic": ['автозапчасти', 'видеоигры', 'напитки', 'продукты питания', 'закуски и приправы', 'аквариум',
                      'одежда', 'уборка', 'электроника', 'образование'],
            "label": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]}

        topics = []
        for index in range(len(predictions)):
            label = predictions[index].item()
            topic = dictionary['topic'][dictionary['label'].index(label)]
            topics.append(topic)
        return topics


class Cashbacker:

    def __init__(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        model_path = os.path.join(current_dir, 'spendings.h5')
        self.cashback_model = load_model(model_path)

    def add_time_features(self, df):
        df['date'] = pd.to_datetime(df['date'])
        df['month'] = df['date'].dt.month
        df['year'] = df['date'].dt.year
        df['season'] = (df['month'] % 12 + 3) // 3  # 1: зима, 2: весна, 3: лето, 4: осень
        return df

    def get_dataframe(self, data):
        topics = ['автозапчасти', 'аквариум', 'видеоигры', 'закуски и приправы', 'напитки', 'образование',
                  'одежда', 'продукты питания', 'уборка', 'электроника']

        new_data = self.add_time_features(data)

        data_grouped = new_data.groupby(['client', 'year', 'month', 'season', 'topic']).agg(
            {'price': 'sum'}).reset_index()
        data_grouped = data_grouped.pivot_table(index=['year', 'month', 'season'], columns='topic', values='price',
                                                fill_value=0).reset_index(drop=True)

        data_grouped = data_grouped.reindex(columns=topics, fill_value=0)

        num_rows_needed = best_look_back - len(data_grouped)

        if num_rows_needed > 0:
            if len(data_grouped) > 0:
                median_values = data_grouped.median()
                for _ in range(num_rows_needed):
                    data_grouped = pd.concat([pd.DataFrame([median_values], columns=topics), data_grouped]).reset_index(
                        drop=True)
            else:
                random_values = {topic: np.random.randint(100, 200) for topic in topics}
                for _ in range(num_rows_needed):
                    data_grouped = pd.concat([pd.DataFrame([random_values], columns=topics), data_grouped]).reset_index(
                        drop=True)

        return data_grouped[topics]

    def cashbaks_for_user(self, data: pd.DataFrame) -> pd.DataFrame:
        categories = pd.DataFrame()
        topics = ['автозапчасти', 'аквариум', 'видеоигры', 'закуски и приправы', 'напитки', 'образование',
                  'одежда', 'продукты питания', 'уборка', 'электроника']

        df = self.get_dataframe(data)

        scaler = StandardScaler().fit(df.values)
        final_scaled_train = scaler.transform(df.values)

        x_test = final_scaled_train[-best_look_back:].reshape(1, best_look_back, -1)

        model = self.cashback_model
        predictions = model.predict(x_test)
        predictions_original = scaler.inverse_transform(predictions)

        for index in range(len(topics)):
            categories.loc[index, 'topics'] = topics[index]
            categories.loc[index, 'predictions'] = predictions_original[0][index]

        top = categories.sort_values(by='predictions', ascending=False).head(5).reset_index(drop=True)

        top.loc[0, 'percent'] = 10
        top.loc[4, 'percent'] = 3

        min_val = top.loc[4, 'predictions']
        max_val = top.loc[0, 'predictions']

        # Рассчёт пропорциональных значений для 2, 3 и 4 мест
        for i in range(1, 4):
            proportion = (top.loc[i, 'predictions'] - min_val) / (max_val - min_val)
            top.loc[i, 'percent'] = round(3 + proportion * (10 - 3))

        cashbacks = top[['topics', 'percent']]

        return cashbacks

cashbacker = Cashbacker()
categorizer = Categorizer()
