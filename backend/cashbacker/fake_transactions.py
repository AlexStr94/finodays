import pandas as pd


def get_fake_transactions():
    df = pd.read_csv('final_ds_finnopolis.csv', names=['product_name', 'inn', 'price', 'user_name'])

    return df[df['user_name'] == 'Блахов Василий Александрович'].to_dict(orient='records')
