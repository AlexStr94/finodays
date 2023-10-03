from tests.config import app
from tests.conftest import TEST_USER


def test_terminal(get_client):
    response = get_client.post(app.url_path_for('get_access_token'), data=TEST_USER)
    assert response.status_code == 200


def test_get_cards(get_client, get_client_credentials):

    headers = {'Authorization': f'Bearer {get_client_credentials}'}
    response = get_client.get(app.url_path_for('get_cards_list'), headers=headers)
    assert response.status_code == 200
