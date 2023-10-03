import pytest

from fastapi.testclient import TestClient

from tests.config import app

from cashbacker.casbacker import Cashbacker, Categories

TEST_USER = {
    'username': 'alex',
    'password': '123456'
}


@pytest.fixture(scope='session')
def get_client():
    with TestClient(app) as client:
        return client


@pytest.fixture(scope='session')
def get_client_credentials(get_client):
    response = get_client.post(app.url_path_for('get_access_token'), data=TEST_USER)
    assert response.status_code == 200
    access_token = response.json().get('access_token')
    return access_token


@pytest.fixture(scope='session')
def get_account_number(get_client, get_client_credentials):
    headers = {'Authorization': f'Bearer {get_client_credentials}'}
    response = get_client.get(app.url_path_for('get_cards_list'), headers=headers)
    assert response.status_code == 200
    account_number = response.json()[0].get('account_number')
    return account_number


@pytest.fixture(scope='session')
def get_cashbacker():
    cashbacker = Cashbacker()
    return cashbacker


@pytest.fixture(scope='session')
def get_categories():
    categories = Categories()
    return categories


@pytest.fixture(scope='session')
def get_spoofing_image():
    with open('tests/files/portret.jpg', 'rb') as file:
        image_data = file.read()
    return image_data
