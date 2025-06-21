# Test-Driven Development Setup for ValMed Backend

This document describes the comprehensive testing setup for the ValMed backend, implementing Test-Driven Development (TDD) with isolated test databases.

## 🏗️ Architecture Overview

### Test Database Isolation
- **Separate SQLite Database**: Each test run uses a fresh `test.db` file
- **Function Scope**: Database is recreated for each test function
- **Automatic Cleanup**: Test database files are automatically removed after tests
- **No Production Impact**: Tests never touch the development or production databases

### Fixture System
- **`db_session`**: Provides isolated database session for each test
- **`client`**: FastAPI TestClient with overridden database dependency
- **Sample Data Fixtures**: Pre-built test data for users, drugs, and orders

## 📁 File Structure

```
backend/
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Test configuration and fixtures
│   └── routers/
│       ├── __init__.py
│       └── test_orders.py       # Orders endpoint tests
├── pytest.ini                  # Pytest configuration
├── run_tests.py                # Test runner script
└── TESTING.md                  # This file
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run All Tests
```bash
python run_tests.py all
```

### 3. Run Specific Test Categories
```bash
# Run only orders router tests
python run_tests.py orders

# Run with coverage report
python run_tests.py coverage

# Clean up test artifacts
python run_tests.py clean
```

## 🧪 Test Categories

### 1. Orders Router Tests (`tests/routers/test_orders.py`)

#### `test_doctor_can_see_only_their_own_orders`
- **Purpose**: Verify doctors can only see their own prescriptions
- **Arrange**: Create two doctors with separate orders
- **Act**: Call `/api/orders/my-orders/` with first doctor's API key
- **Assert**: Verify only one order returned, belonging to correct doctor

#### `test_nurse_cannot_access_doctor_orders_endpoint`
- **Purpose**: Verify role-based access control
- **Arrange**: Create nurse user
- **Act**: Attempt to access doctor-only endpoint with nurse API key
- **Assert**: Verify 403 Forbidden response

#### `test_nurse_and_pharmacist_can_access_active_mar`
- **Purpose**: Verify collaborative access to MAR
- **Arrange**: Create nurse, pharmacist, and active order
- **Act**: Call `/api/orders/active-mar/` with each role's API key
- **Assert**: Verify 200 OK responses for both roles

#### Additional Tests
- `test_doctor_cannot_access_active_mar`: Verify doctors cannot access MAR
- `test_unauthorized_access_without_api_key`: Verify API key requirement
- `test_invalid_api_key_returns_401`: Verify invalid key handling

## 🔧 Configuration Details

### Database Fixture (`conftest.py`)
```python
@pytest.fixture(scope="function")
def db_session():
    # Drop all tables before test
    Base.metadata.drop_all(bind=test_engine)
    
    # Create all tables
    Base.metadata.create_all(bind=test_engine)
    
    # Create a new session
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Clean up test database file after test
        if os.path.exists("test.db"):
            os.remove("test.db")
```

### Test Client Fixture
```python
@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    # Override the database dependency
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Clean up dependency override
    app.dependency_overrides.clear()
```

## 📊 Test Data Fixtures

### Sample Users
- `sample_doctor`: Doctor user with API key `doctor_api_key_123`
- `sample_nurse`: Nurse user with API key `nurse_api_key_456`
- `sample_pharmacist`: Pharmacist user with API key `pharmacist_api_key_789`

### Sample Data
- `sample_drug`: Test drug with 100 units in stock
- `sample_order`: Active medication order for testing

## 🎯 TDD Workflow

### 1. Write Test First
```python
def test_new_feature(self, client, db_session):
    # Arrange
    # Act
    response = client.post("/api/new-endpoint/", json={...})
    # Assert
    assert response.status_code == 200
```

### 2. Run Test (Should Fail)
```bash
python run_tests.py orders
```

### 3. Implement Feature
Add the endpoint/feature to make the test pass.

### 4. Run Test Again (Should Pass)
```bash
python run_tests.py orders
```

### 5. Refactor
Clean up code while ensuring tests still pass.

## 🔍 Running Tests

### Direct Pytest Commands
```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/routers/test_orders.py -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run specific test function
pytest tests/routers/test_orders.py::TestOrdersEndpoints::test_doctor_can_see_only_their_own_orders -v
```

### Using Test Runner Script
```bash
# All available commands
python run_tests.py

# Run specific test categories
python run_tests.py orders
python run_tests.py coverage
python run_tests.py clean
```

## 🛡️ Best Practices

### 1. Test Isolation
- Each test function gets a fresh database
- No shared state between tests
- Automatic cleanup after each test

### 2. Descriptive Test Names
- Use clear, descriptive test function names
- Follow the pattern: `test_<what>_<when>_<expected_result>`

### 3. Arrange-Act-Assert Pattern
```python
def test_example(self, client, db_session):
    # Arrange: Set up test data
    user = create_test_user(db_session)
    
    # Act: Perform the action being tested
    response = client.get("/api/endpoint/", headers={"X-API-Key": user.api_key})
    
    # Assert: Verify the expected outcome
    assert response.status_code == 200
    assert len(response.json()) == 1
```

### 4. Use Fixtures
- Leverage the provided fixtures for common test data
- Create new fixtures for complex test scenarios
- Keep fixtures focused and reusable

## 🚨 Troubleshooting

### Common Issues

#### 1. Database Lock Errors
**Problem**: SQLite database is locked
**Solution**: Ensure proper cleanup in fixtures and use `connect_args={"check_same_thread": False}`

#### 2. Import Errors
**Problem**: Cannot import test modules
**Solution**: Ensure `__init__.py` files exist in test directories

#### 3. Dependency Override Issues
**Problem**: Tests affecting each other
**Solution**: Always clear `app.dependency_overrides` in fixture teardown

### Debug Mode
```bash
# Run tests with debug output
pytest tests/ -v -s --tb=long
```

## 📈 Coverage Reports

Generate coverage reports to identify untested code:
```bash
python run_tests.py coverage
```

This will create:
- Terminal coverage report
- HTML coverage report in `htmlcov/` directory

## 🔄 Continuous Integration

The test setup is designed to work seamlessly with CI/CD pipelines:
- Isolated test databases prevent conflicts
- Automatic cleanup ensures clean test environment
- Clear exit codes for CI integration

## 📝 Adding New Tests

### 1. Create Test File
```python
# tests/routers/test_new_feature.py
import pytest
from fastapi import status

class TestNewFeature:
    def test_new_endpoint(self, client, db_session):
        # Your test implementation
        pass
```

### 2. Add to Test Runner
Update `run_tests.py` to include new test categories if needed.

### 3. Update Documentation
Add test descriptions to this file.

## 🎉 Success Metrics

A successful TDD implementation should achieve:
- ✅ 100% test isolation
- ✅ Fast test execution (< 30 seconds for full suite)
- ✅ Clear test failures with helpful error messages
- ✅ Comprehensive coverage of business logic
- ✅ No test interdependencies
- ✅ Automatic cleanup of test artifacts 