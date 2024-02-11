import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_main_page(client):
    response = client.get('/')
    assert response.status_code == 200

def test_echo_input(client):
    response = client.post('/echo_user_input', data={'user_input': 'Test Input'})
    assert response.status_code == 200
    assert b'You entered: Test Input' in response.data