from app.main import app
from fastapi.testclient import TestClient
import pytest

client = TestClient(app)


@pytest.mark.parametrize("payload, expected_status", [
    ({"user_id": "user123", "password": "pass1234", "email": "user@email.com"}, 200),
    ({"user_id": "ab", "password": "pass1234", "email": "user@email.com"}, 422), 
    ({"user_id": "a"*25, "password": "pass1234", "email": "user@email.com"}, 422),
    ({"user_id": "user123", "password": "short", "email": "user@email.com"}, 422),
    ({"user_id": "user123", "password": "", "email": "user@email.com"}, 422),
    ({"user_id": "user123", "password": "pass1234", "email": "not-an-email"}, 422),
    ({"user_id": "user123", "password": "pass1234"}, 422),
    ({}, 422),
])
def test_register_validation(payload, expected_status):
    response = client.post("/register", json=payload)
    assert response.status_code == expected_status
    
@pytest.mark.parametrize("payload, expected_status", [
    ({"user_id": "dupuser", "password": "pass1234", "email": "a@email.com"}, 200),
    ({"user_id": "dupuser", "password": "pass1234", "email": "a@email.com"}, 400),
])
def test_duplicate_registration(payload, expected_status):
    response = client.post("/register", json=payload)
    assert response.status_code == expected_status

def test_login():
    pass


