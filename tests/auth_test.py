"""
Authentication tests for Florin trading app
Tests registration, login, and token validation
"""

from app.app import app
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

client = TestClient(app)
DB_URL = os.getenv("DB_URL")


@pytest.fixture(scope="function")
def clean_test_db():
    """Clean up test database before each test"""
    engine = create_engine(DB_URL)
    with engine.connect() as connection:
        try:
            connection.execute(text("DELETE FROM users WHERE email NOT LIKE '%admin%'"))
            connection.commit()
        except Exception as e:
            connection.rollback()
    yield
    with engine.connect() as connection:
        try:
            connection.execute(text("DELETE FROM users WHERE email NOT LIKE '%admin%'"))
            connection.commit()
        except Exception as e:
            connection.rollback()


class TestRegistrationValidation:
    
    @pytest.mark.parametrize("payload, expected_status", [
        ({"email": "user@email.com", "password": "pass1234"}, 200),
        ({"email": "not-an-email", "password": "pass1234"}, 422),
        ({"email": "user@email.com", "password": "short"}, 422),
        ({"email": "user@email.com", "password": ""}, 422),
        ({"email": "user@email.com"}, 422),
        ({}, 422),
    ])
    def test_register_validation(self, payload, expected_status, clean_test_db):
        """Test registration payload validation"""
        response = client.post("/register", json=payload)
        assert response.status_code == expected_status
    
    
    def test_duplicate_registration(self, clean_test_db):
        """Test duplicate email registration"""
        email = "duplicate@email.com"
        password = "pass1234"
        
        # First registration should succeed
        response1 = client.post("/register", json={"email": email, "password": password})
        assert response1.status_code == 200
        assert "access_token" in response1.json()
        
        # Second registration with same email should fail
        response2 = client.post("/register", json={"email": email, "password": password})
        assert response2.status_code == 400
        assert "already in use" in response2.json()["detail"]


class TestLogin:
    
    def test_login_success(self, clean_test_db):
        """Test successful login"""
        email = "testuser@email.com"
        password = "testpass123"
        
        # Register user
        client.post("/register", json={"email": email, "password": password})
        
        # Login
        response = client.post("/login", json={"email": email, "password": password})
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_wrong_password(self, clean_test_db):
        """Test login with incorrect password"""
        email = "testuser@email.com"
        password = "testpass123"
        
        # Register user
        client.post("/register", json={"email": email, "password": password})
        
        # Try login with wrong password
        response = client.post("/login", json={"email": email, "password": "wrongpass"})
        assert response.status_code == 401
        assert "credentials" in response.json()["detail"].lower()
    
    def test_login_nonexistent_user(self, clean_test_db):
        """Test login with non-existent email"""
        response = client.post("/login", json={
            "email": "nonexistent@email.com",
            "password": "anypass123"
        })
        assert response.status_code == 401


class TestTokenValidation:
    
    def test_protected_endpoint_no_token(self, clean_test_db):
        """Test protected endpoint without token"""
        response = client.get("/portfolio")
        assert response.status_code == 403
    
    def test_protected_endpoint_invalid_token(self, clean_test_db):
        """Test protected endpoint with invalid token"""
        response = client.get("/portfolio", 
            headers={"Authorization": "Bearer invalid_token_123"}
        )
        assert response.status_code == 401
    
    def test_protected_endpoint_with_valid_token(self, clean_test_db):
        """Test protected endpoint with valid token"""
        email = "tokentest@email.com"
        password = "testpass123"
        
        # Register
        register_response = client.post("/register", json={"email": email, "password": password})
        token = register_response.json()["access_token"]
        
        # Access protected endpoint
        response = client.get("/portfolio",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200


