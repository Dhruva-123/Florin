"""Parametrized endpoint tests for the implemented Florin API routes."""

import pytest
from fastapi.testclient import TestClient

from app.app import app


client = TestClient(app)


VALID_USERS = [
    (f"user-{number}", f"user{number}@example.com")
    for number in range(1, 11)
]


INVALID_REGISTRATION_PAYLOADS = [
    {"email": "user@example.com", "password": "password123"},
    {"user_id": "ab", "email": "user@example.com", "password": "password123"},
    {"user_id": "valid-user", "email": "bad-email", "password": "password123"},
    {"user_id": "valid-user", "email": "user@example.com", "password": "short"},
    {"user_id": "valid-user", "email": "user@example.com", "password": ""},
    {"user_id": "valid-user", "email": "user@example.com"},
    {"user_id": "valid-user", "password": "password123"},
    {"user_id": "valid-user", "email": "user@example.com", "password": "x" * 61},
    {"user_id": "valid-user", "email": None, "password": "password123"},
    {},
]


INVALID_ORDER_PAYLOADS = [
    {"symbol": "TE", "quantity": 1, "price": 10},
    {"symbol": "TOOLONG", "quantity": 1, "price": 10},
    {"symbol": "TEST", "quantity": 0, "price": 10},
    {"symbol": "TEST", "quantity": -1, "price": 10},
    {"symbol": "TEST", "quantity": 1, "price": -10},
    {"symbol": "TEST", "quantity": 1, "price": "not-a-number"},
    {"symbol": "TEST", "quantity": "many", "price": 10},
    {"symbol": "TEST", "price": 10},
    {"symbol": "TEST", "quantity": 1},
    {},
]


INVALID_TOKENS = [f"invalid-token-{number}" for number in range(1, 11)]


def auth_payload(user_id, email=None, password="password123"):
    return {
        "user_id": user_id,
        "email": email or f"{user_id}@example.com",
        "password": password,
    }


def register_user(user_id, email=None):
    response = client.post("/register", json=auth_payload(user_id, email))
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.mark.parametrize("user_id,email", VALID_USERS)
def test_register_returns_token_for_ten_users(user_id, email):
    response = client.post("/register", json=auth_payload(user_id, email))

    assert response.status_code == 200
    assert isinstance(response.json()["access_token"], str)


@pytest.mark.parametrize("payload", INVALID_REGISTRATION_PAYLOADS)
def test_register_rejects_invalid_payloads(payload):
    response = client.post("/register", json=payload)

    assert response.status_code == 422


@pytest.mark.parametrize("user_id,email", VALID_USERS)
def test_register_rejects_duplicate_emails(user_id, email):
    register_user(user_id, email)

    response = client.post("/register", json=auth_payload(f"other-{user_id}", email))

    assert response.status_code == 400


@pytest.mark.parametrize("user_id,email", VALID_USERS)
def test_login_returns_token_for_ten_users(user_id, email):
    register_user(user_id, email)

    response = client.post("/login", json=auth_payload(user_id, email))

    assert response.status_code == 200
    assert isinstance(response.json()["access_token"], str)


@pytest.mark.parametrize("user_id", [f"missing-{number}" for number in range(1, 11)])
def test_login_rejects_unknown_users(user_id):
    response = client.post("/login", json=auth_payload(user_id))

    assert response.status_code == 401


@pytest.mark.parametrize("user_id", [f"wrong-password-{number}" for number in range(1, 11)])
def test_login_rejects_wrong_passwords(user_id):
    register_user(user_id)

    response = client.post(
        "/login",
        json=auth_payload(user_id, password="wrong-password"),
    )

    assert response.status_code == 401


@pytest.mark.parametrize("endpoint", ["/portfolio"] * 10)
def test_portfolio_requires_authentication(endpoint):
    response = client.get(endpoint)

    assert response.status_code == 401


@pytest.mark.parametrize("token", INVALID_TOKENS)
def test_portfolio_rejects_invalid_tokens(token):
    response = client.get(
        "/portfolio",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401


@pytest.mark.parametrize("user_id", [f"portfolio-{number}" for number in range(1, 11)])
def test_portfolio_accepts_registered_tokens(user_id):
    token = register_user(user_id)

    response = client.get(
        "/portfolio",
        headers={"Authorization": f"Bearer {str(token)}"},
    )

    assert response.status_code == 200
    assert "balance" in response.json()
    assert isinstance(response.json()["holdings"], list)


@pytest.mark.parametrize("user_id", [f"news-{number}" for number in range(1, 11)])
def test_news_returns_empty_list_for_registered_users(user_id):
    token = register_user(user_id)

    response = client.get(
        "/news",
        headers={"Authorization": f"Bearer {str(token)}"},
    )

    assert response.status_code == 200
    assert response.json()["news"] == []


@pytest.mark.parametrize("endpoint", ["/news"] * 10)
def test_news_requires_authentication(endpoint):
    response = client.get(endpoint)

    assert response.status_code == 401


@pytest.mark.parametrize("payload", INVALID_ORDER_PAYLOADS)
def test_buy_rejects_invalid_payloads(payload):
    response = client.post("/buy", json=payload)

    assert response.status_code in (401, 422)


@pytest.mark.parametrize("payload", INVALID_ORDER_PAYLOADS)
def test_sell_rejects_invalid_payloads(payload):
    response = client.post("/sell", json=payload)

    assert response.status_code in (401, 422)


@pytest.mark.parametrize("endpoint", ["/buy", "/sell"] * 5)
def test_order_endpoints_require_authentication(endpoint):
    response = client.post(
        endpoint,
        json={"symbol": "TEST", "quantity": 1, "price": 10},
    )

    assert response.status_code == 401


@pytest.mark.parametrize("number", range(1, 11))
def test_market_returns_empty_order_groups(number):
    response = client.get("/market")

    assert response.status_code == 200
    assert isinstance(response.json()["Buy Orders"], dict)
    assert isinstance(response.json()["Sell Orders"], dict)


@pytest.mark.parametrize("number", range(1, 11))
def test_trade_history_requires_authentication(number):
    response = client.get("/trade_history")

    assert response.status_code == 401


@pytest.mark.parametrize("user_id", [f"regular-{number}" for number in range(1, 11)])
def test_trade_history_rejects_regular_users(user_id):
    token = register_user(user_id)

    response = client.get(
        "/trade_history",
        headers={"Authorization": f"Bearer {str(token)}"},
    )

    assert response.status_code == 403
