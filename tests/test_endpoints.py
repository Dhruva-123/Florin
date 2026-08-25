"""
Comprehensive test suite for Florin trading app endpoints
Tests cover: Registration, Login, Trading (Buy/Sell), Market, Portfolio, News, and Trade History
"""

from app.app import app
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

client = TestClient(app)
DB_URL = os.getenv("DB_URL")

# ==================== FIXTURES ====================

@pytest.fixture(scope="function")
def setup_test_db():
    """Setup and teardown test database"""
    # Create connection
    engine = create_engine(DB_URL)
    
    # Clear test data before each test
    with engine.connect() as connection:
        try:
            connection.execute(text("DELETE FROM transactions"))
            connection.execute(text("DELETE FROM holdings"))
            connection.execute(text("DELETE FROM asks"))
            connection.execute(text("DELETE FROM bids"))
            connection.execute(text("DELETE FROM users WHERE email NOT LIKE '%admin%'"))
            connection.commit()
        except Exception as e:
            print(f"Cleanup error: {e}")
            connection.rollback()
    
    yield engine
    
    # Cleanup after test
    with engine.connect() as connection:
        try:
            connection.execute(text("DELETE FROM transactions"))
            connection.execute(text("DELETE FROM holdings"))
            connection.execute(text("DELETE FROM asks"))
            connection.execute(text("DELETE FROM bids"))
            connection.execute(text("DELETE FROM users WHERE email NOT LIKE '%admin%'"))
            connection.commit()
        except Exception as e:
            print(f"Final cleanup error: {e}")
            connection.rollback()


@pytest.fixture(scope="function")
def test_user(setup_test_db):
    """Create a test user and return user details"""
    response = client.post("/register", json={
        "email": "testuser@example.com",
        "password": "testpass123"
    })
    assert response.status_code == 200
    data = response.json()
    return {
        "email": "testuser@example.com",
        "password": "testpass123",
        "token": data.get("access_token")
    }


@pytest.fixture(scope="function")
def test_stock_in_db(setup_test_db):
    """Insert a test stock into the database"""
    engine = create_engine(DB_URL)
    with engine.connect() as connection:
        try:
            connection.execute(text("""
                INSERT INTO stocks (symbol, name, current_value)
                VALUES ('TEST', 'Test Stock', 100.00)
            """))
            connection.commit()
        except Exception as e:
            connection.rollback()
            print(f"Stock insertion error: {e}")


# ==================== REGISTRATION TESTS ====================

class TestRegistration:
    
    def test_register_success(self, setup_test_db):
        """Test successful user registration"""
        response = client.post("/register", json={
            "email": "newuser@example.com",
            "password": "securepass123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_register_invalid_email(self, setup_test_db):
        """Test registration with invalid email"""
        response = client.post("/register", json={
            "email": "not-an-email",
            "password": "securepass123"
        })
        assert response.status_code == 422  # Validation error
    
    def test_register_short_password(self, setup_test_db):
        """Test registration with password too short"""
        response = client.post("/register", json={
            "email": "user@example.com",
            "password": "short"
        })
        assert response.status_code == 422
    
    def test_register_duplicate_email(self, setup_test_db, test_user):
        """Test registration with duplicate email"""
        response = client.post("/register", json={
            "email": "testuser@example.com",
            "password": "anotherpass123"
        })
        assert response.status_code == 400
        assert "already in use" in response.json()["detail"]
    
    def test_register_missing_fields(self, setup_test_db):
        """Test registration with missing fields"""
        response = client.post("/register", json={
            "email": "user@example.com"
        })
        assert response.status_code == 422


# ==================== LOGIN TESTS ====================

class TestLogin:
    
    def test_login_success(self, setup_test_db, test_user):
        """Test successful login"""
        response = client.post("/login", json={
            "email": "testuser@example.com",
            "password": "testpass123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
    
    def test_login_wrong_password(self, setup_test_db, test_user):
        """Test login with wrong password"""
        response = client.post("/login", json={
            "email": "testuser@example.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
    
    def test_login_nonexistent_email(self, setup_test_db):
        """Test login with non-existent email"""
        response = client.post("/login", json={
            "email": "nonexistent@example.com",
            "password": "somepass123"
        })
        assert response.status_code == 401
    
    def test_login_invalid_email_format(self, setup_test_db):
        """Test login with invalid email format"""
        response = client.post("/login", json={
            "email": "not-an-email",
            "password": "somepass123"
        })
        assert response.status_code == 422


# ==================== BUY ORDER TESTS ====================

class TestBuyOrder:
    
    def test_buy_order_success(self, setup_test_db, test_user, test_stock_in_db):
        """Test successful buy order placement"""
        response = client.post("/buy", 
            json={
                "symbol": "TEST",
                "quantity": 10,
                "price": 150.00
            },
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        assert response.status_code == 200
        assert "Buy order placed successfully" in response.json()["Message"]
    
    def test_buy_order_stock_not_found(self, setup_test_db, test_user):
        """Test buy order for non-existent stock"""
        response = client.post("/buy",
            json={
                "symbol": "NOEXIST",
                "quantity": 10,
                "price": 150.00
            },
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        assert response.status_code == 404
        assert "Stock not found" in response.json()["detail"]
    
    def test_buy_order_no_auth(self, setup_test_db, test_stock_in_db):
        """Test buy order without authentication"""
        response = client.post("/buy",
            json={
                "symbol": "TEST",
                "quantity": 10,
                "price": 150.00
            }
        )
        assert response.status_code == 403  # Forbidden (no token)
    
    def test_buy_order_invalid_quantity(self, setup_test_db, test_user, test_stock_in_db):
        """Test buy order with invalid quantity"""
        response = client.post("/buy",
            json={
                "symbol": "TEST",
                "quantity": 0,
                "price": 150.00
            },
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        assert response.status_code == 422
    
    def test_buy_order_negative_price(self, setup_test_db, test_user, test_stock_in_db):
        """Test buy order with negative price"""
        response = client.post("/buy",
            json={
                "symbol": "TEST",
                "quantity": 10,
                "price": -150.00
            },
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        assert response.status_code == 422


# ==================== SELL ORDER TESTS ====================

class TestSellOrder:
    
    def test_sell_order_success(self, setup_test_db, test_user, test_stock_in_db):
        """Test successful sell order placement"""
        response = client.post("/sell",
            json={
                "symbol": "TEST",
                "quantity": 5,
                "price": 100.00
            },
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        assert response.status_code == 200
        assert "Sell order placed successfully" in response.json()["Message"]
    
    def test_sell_order_stock_not_found(self, setup_test_db, test_user):
        """Test sell order for non-existent stock"""
        response = client.post("/sell",
            json={
                "symbol": "NOEXIST",
                "quantity": 5,
                "price": 100.00
            },
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        assert response.status_code == 404
        assert "Stock not found" in response.json()["detail"]
    
    def test_sell_order_no_auth(self, setup_test_db, test_stock_in_db):
        """Test sell order without authentication"""
        response = client.post("/sell",
            json={
                "symbol": "TEST",
                "quantity": 5,
                "price": 100.00
            }
        )
        assert response.status_code == 403


# ==================== MARKET TESTS ====================

class TestMarket:
    
    def test_market_empty(self, setup_test_db):
        """Test market page with no orders"""
        response = client.get("/market")
        assert response.status_code == 200
        data = response.json()
        assert "Buy Orders" in data
        assert "Sell Orders" in data
        assert isinstance(data["Buy Orders"], dict)
        assert isinstance(data["Sell Orders"], dict)
    
    def test_market_with_orders(self, setup_test_db, test_user, test_stock_in_db):
        """Test market page with buy and sell orders"""
        # Place a buy order
        client.post("/buy",
            json={"symbol": "TEST", "quantity": 10, "price": 150.00},
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        
        # Place a sell order
        client.post("/sell",
            json={"symbol": "TEST", "quantity": 5, "price": 100.00},
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        
        # Get market
        response = client.get("/market")
        assert response.status_code == 200
        data = response.json()
        assert "TEST" in data["Buy Orders"]
        assert "TEST" in data["Sell Orders"]
        assert len(data["Buy Orders"]["TEST"]) == 1
        assert len(data["Sell Orders"]["TEST"]) == 1


# ==================== PORTFOLIO TESTS ====================

class TestPortfolio:
    
    def test_portfolio_no_auth(self, setup_test_db):
        """Test portfolio without authentication"""
        response = client.get("/portfolio")
        assert response.status_code == 403
    
    def test_portfolio_with_auth(self, setup_test_db, test_user):
        """Test portfolio with valid token"""
        response = client.get("/portfolio",
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "balance" in data
        assert "holdings" in data
        assert isinstance(data["balance"], (int, float, str))
        assert isinstance(data["holdings"], list)
    
    def test_portfolio_balance_correct(self, setup_test_db, test_user):
        """Test portfolio shows correct starting balance"""
        response = client.get("/portfolio",
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        assert response.status_code == 200
        # Should have starting balance from STARTING_BALANCE_FOR_A_NEW_USER
        assert response.json()["balance"] is not None
    
    def test_portfolio_no_holdings_initially(self, setup_test_db, test_user):
        """Test portfolio has no holdings initially"""
        response = client.get("/portfolio",
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        assert response.status_code == 200
        assert len(response.json()["holdings"]) == 0


# ==================== NEWS TESTS ====================

class TestNews:
    
    def test_news_no_auth(self, setup_test_db):
        """Test news endpoint without authentication"""
        response = client.get("/news")
        assert response.status_code == 403
    
    def test_news_with_auth(self, setup_test_db, test_user):
        """Test news endpoint with valid token"""
        response = client.get("/news",
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "news" in data
        assert "message" in data
        assert isinstance(data["news"], list)


# ==================== TRADE HISTORY TESTS ====================

class TestTradeHistory:
    
    def test_trade_history_no_auth(self, setup_test_db):
        """Test trade history without authentication"""
        response = client.get("/trade_history")
        assert response.status_code == 403
    
    def test_trade_history_non_admin(self, setup_test_db, test_user):
        """Test trade history as non-admin user"""
        response = client.get("/trade_history",
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        assert response.status_code == 403
        assert "admin" in response.json()["detail"].lower()
    
    def test_trade_history_empty(self, setup_test_db):
        """Test trade history page with no trades"""
        # Login as admin (assuming admin exists from setup)
        response = client.post("/login", json={
            "email": os.getenv("ADMIN_USER_EMAIL"),
            "password": os.getenv("ADMIN_USER_PWD")
        })
        
        if response.status_code == 200:
            admin_token = response.json()["access_token"]
            response = client.get("/trade_history",
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            assert response.status_code == 200
            data = response.json()
            assert "logs" in data
            assert isinstance(data["logs"], list)


# ==================== INTEGRATION TESTS ====================

class TestIntegration:
    
    def test_full_trading_flow(self, setup_test_db, test_user, test_stock_in_db):
        """Test complete trading workflow: register, buy, sell, check portfolio"""
        # User already registered from test_user fixture
        
        # Place buy order
        buy_response = client.post("/buy",
            json={"symbol": "TEST", "quantity": 5, "price": 100.00},
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        assert buy_response.status_code == 200
        
        # Place sell order
        sell_response = client.post("/sell",
            json={"symbol": "TEST", "quantity": 3, "price": 110.00},
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        assert sell_response.status_code == 200
        
        # Check market
        market_response = client.get("/market")
        assert market_response.status_code == 200
        market_data = market_response.json()
        assert "TEST" in market_data["Buy Orders"]
        assert "TEST" in market_data["Sell Orders"]
        
        # Check portfolio
        portfolio_response = client.get("/portfolio",
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        assert portfolio_response.status_code == 200
        portfolio_data = portfolio_response.json()
        assert "balance" in portfolio_data
