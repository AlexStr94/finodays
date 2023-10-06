import pandas as pd


def test_add_time_features(get_cashbacker):
    data = pd.DataFrame({
        'date': ['2023-01-01', '2023-02-01', '2023-03-01'],
    })
    df_with_time_features = get_cashbacker.add_time_features(data)
    assert df_with_time_features.shape == (3, 4)


def test_get_dataframe(get_cashbacker):
    data = pd.DataFrame({
        'date': ['2023-01-01', '2023-01-01', '2023-02-01'],
        'client': ['client1', 'client2', 'client1'],
        'topic': ['topic1', 'topic2', 'topic1'],
        'price': [100, 200, 150],
    })
    data_grouped = get_cashbacker.get_dataframe(data)
    assert data_grouped.shape == (22, 10)


def test_cashbaks_for_user(get_cashbacker):
    data = pd.DataFrame({
        'date': ['2023-01-01', '2023-01-01', '2023-02-01'],
        'client': ['client1', 'client2', 'client1'],
        'topic': ['topic1', 'topic2', 'topic1'],
        'price': [100, 200, 150],
    })
    cashbacks = get_cashbacker.cashbaks_for_user(data)
    assert cashbacks.shape == (5, 2)
