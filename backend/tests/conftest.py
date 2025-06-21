import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from database import Base, SessionLocal
from dependencies import get_db, get_current_user
from main import app
import secrets
from models import User, UserRole, Drug, MedicationOrder, OrderStatus
from datetime import datetime

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db_session, request):
    """Create a test client with dependency override. Allows per-test user override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    # Allow per-test override of get_current_user
    user_override = getattr(request, 'param', None)
    if user_override:
        app.dependency_overrides[get_current_user] = lambda: user_override

    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def test_user_doctor(db_session):
    """Create a test doctor user."""
    user = User(
        email="doctor@test.com",
        role=UserRole.doctor,
        api_key=secrets.token_hex(16),
        hashed_password="hashed_password"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def test_user_nurse(db_session):
    """Create a test nurse user."""
    user = User(
        email="nurse@test.com",
        role=UserRole.nurse,
        api_key=secrets.token_hex(16),
        hashed_password="hashed_password"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def test_user_pharmacist(db_session):
    """Create a test pharmacist user."""
    user = User(
        email="pharmacist@test.com",
        role=UserRole.pharmacist,
        api_key=secrets.token_hex(16),
        hashed_password="hashed_password"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def test_drug(db_session):
    """Create a test drug."""
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
def test_order(db_session, test_user_doctor, test_drug):
    """Create a test medication order."""
    order = MedicationOrder(
        patient_name="John Doe",
        drug_id=test_drug.id,
        dosage=2,
        schedule="Every 8 hours",
        status=OrderStatus.active,
        doctor_id=test_user_doctor.id,
        created_at=datetime.utcnow()
    )
    db_session.add(order)
    db_session.commit()
    db_session.refresh(order)
    return order

@pytest.fixture
def override_user(request, test_user_doctor, test_user_nurse, test_user_pharmacist):
    """Fixture to override get_current_user for a specific role in a test."""
    role = getattr(request, 'param', None)
    if role == 'doctor':
        return test_user_doctor
    elif role == 'nurse':
        return test_user_nurse
    elif role == 'pharmacist':
        return test_user_pharmacist
    return None 