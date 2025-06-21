import pytest
import os
import tempfile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from database import Base, get_db
from main import app
from models import User, UserRole, Drug, MedicationOrder, OrderStatus
import secrets
from dependencies import get_current_user
from fastapi import Security
from fastapi.security.api_key import APIKeyHeader

# Test database configuration
TEST_DATABASE_URL = "sqlite:///./test.db"

# Remove test.db before each test session
@pytest.fixture(scope="session", autouse=True)
def cleanup_test_db():
    try:
        os.remove("./test.db")
    except FileNotFoundError:
        pass
    yield
    try:
        os.remove("./test.db")
    except FileNotFoundError:
        pass

# Create test engine
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}  # Required for SQLite
)

print(f"DEBUG: Test engine created with URL: {test_engine.url}")

# Create test session factory
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="function")
def db_session(cleanup_test_db):
    """
    Create a fresh database session for each test.
    This fixture ensures each test runs in isolation.
    """
    print(f"DEBUG: Creating test database session with engine URL: {test_engine.url}")
    
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

@pytest.fixture(scope="function")
def client(db_session):
    """
    Create a test client with overridden database and user dependencies.
    This ensures tests use the isolated test database and test users for authentication.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass  # Session cleanup is handled by db_session fixture

    api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

    def override_get_current_user(api_key: str = Security(api_key_header)):
        if not api_key:
            from fastapi import HTTPException, status
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing API Key")
        
        try:
            user = db_session.query(User).filter(User.api_key == api_key).first()
            if not user:
                from fastapi import HTTPException, status
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key")
            return user
        except Exception as e:
            # Handle cases where tables don't exist yet or other DB errors
            from fastapi import HTTPException, status
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key")

    # Override the database and user dependencies
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as test_client:
        yield test_client

    # Clean up dependency overrides
    app.dependency_overrides.clear()

@pytest.fixture
def sample_doctor(db_session):
    """Create a sample doctor user for testing."""
    doctor = User(
        email="doctor@test.com",
        hashed_password="hashed_password",
        api_key="doctor_api_key_123",
        role=UserRole.doctor
    )
    db_session.add(doctor)
    db_session.commit()
    db_session.refresh(doctor)
    return doctor

@pytest.fixture
def sample_nurse(db_session):
    """Create a sample nurse user for testing."""
    nurse = User(
        email="nurse@test.com",
        hashed_password="hashed_password",
        api_key="nurse_api_key_456",
        role=UserRole.nurse
    )
    db_session.add(nurse)
    db_session.commit()
    db_session.refresh(nurse)
    return nurse

@pytest.fixture
def sample_pharmacist(db_session):
    """Create a sample pharmacist user for testing."""
    pharmacist = User(
        email="pharmacist@test.com",
        hashed_password="hashed_password",
        api_key="pharmacist_api_key_789",
        role=UserRole.pharmacist
    )
    db_session.add(pharmacist)
    db_session.commit()
    db_session.refresh(pharmacist)
    return pharmacist

@pytest.fixture
def sample_drug(db_session):
    """Create a sample drug for testing."""
    drug = Drug(
        name="Test Drug",
        form="Tablet",
        strength="500mg",
        current_stock=100,
        low_stock_threshold=10
    )
    db_session.add(drug)
    db_session.commit()
    db_session.refresh(drug)
    return drug

@pytest.fixture
def sample_order(db_session, sample_doctor, sample_drug):
    """Create a sample medication order for testing."""
    order = MedicationOrder(
        patient_name="John Doe",
        drug_id=sample_drug.id,
        dosage=2,
        schedule="Every 8 hours",
        status=OrderStatus.active,
        doctor_id=sample_doctor.id
    )
    db_session.add(order)
    db_session.commit()
    db_session.refresh(order)
    return order

@pytest.fixture
def test_user_doctor(sample_doctor):
    return sample_doctor

@pytest.fixture
def test_user_nurse(sample_nurse):
    return sample_nurse

@pytest.fixture
def test_user_pharmacist(sample_pharmacist):
    return sample_pharmacist

@pytest.fixture
def test_order(sample_order):
    return sample_order

@pytest.fixture
def test_drug(sample_drug):
    return sample_drug 