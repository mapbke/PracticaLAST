import re
import pytest
from app import create_app

@pytest.fixture
def app(tmp_path):
    return create_app({'TESTING': True, 'SECRET_KEY': 'test-only-key', 'DATABASE': str(tmp_path / 'test.db'), 'FORCE_HTTPS': False})

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def headers(client):
    html = client.get('/').get_data(as_text=True)
    token = re.search(r'name="csrf-token" content="([^"]+)"', html).group(1)
    return {'X-CSRFToken': token}
