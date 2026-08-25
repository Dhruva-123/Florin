"""
Pytest configuration and fixtures for Florin trading app tests
"""

import pytest
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

load_dotenv()

@pytest.fixture(scope="session", autouse=True)
def check_database():
    """Check if database is available at test start"""
    DB_URL = os.getenv("DB_URL")
    
    if not DB_URL:
        pytest.skip("DB_URL not configured in .env")
    
    try:
        engine = create_engine(DB_URL)
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        print("✓ Database connection verified")
        return True
    except OperationalError as e:
        pytest.fail(f"Cannot connect to database: {e}\n"
                   f"Make sure MySQL is running and DB_URL is correct in .env")
    except Exception as e:
        pytest.fail(f"Database check failed: {e}")


@pytest.fixture(scope="function")
def db_session():
    """Provide a database connection for tests"""
    DB_URL = os.getenv("DB_URL")
    engine = create_engine(DB_URL)
    
    with engine.connect() as connection:
        yield connection


@pytest.fixture(scope="function", autouse=True)
def reset_test_tables():
    """Reset test tables before each test"""
    DB_URL = os.getenv("DB_URL")
    if not DB_URL:
        return
    
    engine = create_engine(DB_URL)
    
    # Tables to clear (in reverse dependency order)
    tables_to_clear = [
        "transactions",
        "holdings",
        "asks",
        "bids",
    ]
    
    with engine.connect() as connection:
        try:
            for table in tables_to_clear:
                connection.execute(text(f"DELETE FROM {table}"))
            
            # Keep admin user but delete test users
            connection.execute(text("DELETE FROM users WHERE email NOT LIKE '%admin%'"))
            
            connection.commit()
        except Exception as e:
            print(f"Warning: Could not reset tables: {e}")
            connection.rollback()
    
    yield
    
    # Cleanup after test
    with engine.connect() as connection:
        try:
            for table in tables_to_clear:
                connection.execute(text(f"DELETE FROM {table}"))
            connection.execute(text("DELETE FROM users WHERE email NOT LIKE '%admin%'"))
            connection.commit()
        except Exception as e:
            print(f"Warning: Could not cleanup after test: {e}")
            connection.rollback()


def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
