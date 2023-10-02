import pytest

from fastapi.testclient import TestClient

from tests.config import app


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
