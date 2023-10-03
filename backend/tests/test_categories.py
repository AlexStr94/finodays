import pandas as pd


def test_add_time_features(get_categories):
    data = pd.DataFrame({
        'date': ['2023-01-01', '2023-02-01', '2023-03-01'],
    })
    df_with_time_features = get_categories.add_time_features(data)
    assert df_with_time_features.shape == (3, 4)


def test_get_dataframe(get_categories):
    data = pd.DataFrame({
        'date': ['2023-01-01', '2023-01-01', '2023-02-01'],
        'client': ['client1', 'client2', 'client1'],
        'topic': ['topic1', 'topic2', 'topic1'],
        'price': [100, 200, 150],
    })
    data_grouped = get_categories.get_dataframe(data)
    assert data_grouped.shape == (2, 2)
    assert data_grouped.values.tolist() == [[100, 200], [150, 0]]


# Бага ValueError: cannot reshape array of size 4 into shape (1,22,newaxis)с
def test_cashbaks_for_user(get_categories):
    data = pd.DataFrame({
        'date': ['2023-01-01', '2023-01-01', '2023-02-01'],
        'client': ['client1', 'client2', 'client1'],
        'topic': ['topic1', 'topic2', 'topic1'],
        'price': [100, 200, 150],
    })
    cashbacks = get_categories.cashbaks_for_user(data)
    assert cashbacks.shape == (5, 2)
