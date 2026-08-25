# Florin Trading App - Test Suite

## Overview
Comprehensive test suite for all endpoints in the Florin trading application.

**Test Files:**
- `auth_test.py` - Authentication and token validation tests
- `test_endpoints.py` - Complete endpoint test coverage

## Test Coverage

### Authentication Tests (`auth_test.py`)
- ✅ Registration validation (email, password, required fields)
- ✅ Duplicate email handling
- ✅ Login success and failure cases
- ✅ Token validation for protected endpoints
- ✅ Invalid/missing token handling

### Endpoint Tests (`test_endpoints.py`)

#### Registration
- Successful registration
- Invalid email validation
- Short password validation
- Duplicate email rejection
- Missing field validation

#### Login
- Successful login with correct credentials
- Failed login with wrong password
- Non-existent user login
- Invalid email format

#### Buy Orders
- Successful buy order placement
- Non-existent stock error
- Missing authentication error
- Invalid quantity validation
- Negative price validation

#### Sell Orders
- Successful sell order placement
- Non-existent stock error
- Missing authentication error

#### Market
- Empty market state
- Market with active orders
- Buy/Sell orders organized by symbol

#### Portfolio
- Portfolio access without auth
- Portfolio with valid token
- Correct balance display
- Initial holdings verification

#### News
- News access without auth
- News access with valid token

#### Trade History
- Trade history access without auth
- Non-admin user rejection
- Empty trade history
- Admin user access

#### Integration Tests
- Complete trading flow (register → buy → sell → portfolio check)

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test File
```bash
pytest tests/auth_test.py
pytest tests/test_endpoints.py
```

### Run Specific Test Class
```bash
pytest tests/test_endpoints.py::TestBuyOrder
```

### Run Specific Test
```bash
pytest tests/test_endpoints.py::TestBuyOrder::test_buy_order_success
```

### Run with Verbose Output
```bash
pytest -v
```

### Run with Coverage Report
```bash
pip install pytest-cov
pytest --cov=app --cov-report=html
```

### Run Only Integration Tests
```bash
pytest -m integration
```

## Setup

1. **Database**: Tests use your configured MySQL database. A test fixture automatically cleans up before and after each test.

2. **Environment**: Make sure `.env` is configured with:
   ```env
   DB_URL=mysql+mysql-connector-python://root:password@localhost:3306/florin
   SECRET_KEY=your-secret-key
   ADMIN_USER_EMAIL=admin@florin.com
   ADMIN_USER_PWD=admin_password
   STARTING_BALANCE_FOR_A_NEW_USER=10000
   ```

3. **Database Ready**: Ensure your database tables exist (they're created by the app on startup)

4. **Stock Data**: The `test_stock_in_db` fixture creates a `TEST` stock for testing. You need real stocks in the database for full integration tests.

## Notes

- Each test gets a clean database state via fixtures
- Test users are automatically created and cleaned up
- Tests are isolated and can run in any order
- Protected endpoints require valid JWT tokens
- Admin endpoints require admin user credentials

## Common Issues

**Issue**: "Database Error" in tests
- **Solution**: Ensure MySQL is running and DB_URL is correct

**Issue**: Tests pass individually but fail when run together
- **Solution**: Check if fixtures are cleaning up properly. The `clean_test_db` fixture should reset state.

**Issue**: Can't connect to database
- **Solution**: Verify DB_URL in .env matches your MySQL setup

## Future Enhancements

- [ ] Mock external services (news API)
- [ ] Performance tests for trading engine
- [ ] Load testing for market endpoint
- [ ] E2E tests with real order matching
