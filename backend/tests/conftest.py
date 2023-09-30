import pytest

from fastapi.testclient import TestClient

from tests.config import app


@pytest.fixture(scope='session')
def get_client():
    client = TestClient(app)
    return client
