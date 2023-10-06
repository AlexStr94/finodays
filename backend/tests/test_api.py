from datetime import date

from tests.config import app
from tests.conftest import TEST_USER


def test_get_access_token(get_client):
    response = get_client.post(app.url_path_for('get_access_token'), data=TEST_USER)
    assert response.status_code == 200
    assert 'access_token' in response.json().keys()


def test_get_cards_list(get_client, get_client_credentials):
    headers = {'Authorization': f'Bearer {get_client_credentials}'}
    response = get_client.get(app.url_path_for('get_cards_list'), headers=headers)
    assert response.status_code == 200
    assert 'cards' in response.json()[0].keys()


def test_get_transactions(get_client, get_client_credentials):
    headers = {"Authorization": f"Bearer {get_client_credentials}"}
    response = get_client.get(app.url_path_for('get_transactions'), headers=headers)
    assert response.status_code == 200
    assert 'transactions' in response.json()[0].keys()


def test_get_cashback_for_choose(get_client, get_client_credentials, get_account_number):
    headers = {'Authorization': f'Bearer {get_client_credentials}'}

    response = get_client.get(f'{app.url_path_for("get_cashback_for_choose")}?account_number={get_account_number}',
                              headers=headers)

    assert response.status_code == 202
    assert 'cashbacks' in response.json().keys()


def test_choose_cashback(get_client, get_client_credentials, get_account_number, get_client_cashback):
    headers = {'Authorization': f'Bearer {get_client_credentials}'}
    json_data = {
        "account_number": get_account_number,
        "month": date.today().isoformat(),
        "cashback": get_client_cashback[:3]
    }
    response = get_client.post(app.url_path_for('choose_card_cashback'), json=json_data, headers=headers)
    assert response.status_code == 200
