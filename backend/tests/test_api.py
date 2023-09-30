from tests.config import app


TEST_USER = {
    'username': 'alex',
    'password': '123456'
}

def test_terminal(get_client):
    response = get_client.post(app.url_path_for('get_access_token'), data=TEST_USER)

    assert response.status_code == 200
