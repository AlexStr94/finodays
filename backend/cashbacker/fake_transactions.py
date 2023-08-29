import os

import pandas as pd


def get_fake_transactions():
    file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'final_ds_finnopolis.csv')
    df = pd.read_csv(file, names=['product_name', 'inn', 'price', 'user_name'])

    return df[df['user_name'] == 'Блахов Василий Александрович'].to_dict(orient='records')
