import pytest
from fastapi import status

def test_basic_setup_works(client):
    """Test that the basic test setup is working."""
    # Test that the health endpoint works
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "healthy"

def test_database_isolation(db_session):
    """Test that database isolation is working."""
    # This test should have its own isolated database
    assert db_session is not None
    
    # Test that we can query the database
    from models import User
    users = db_session.query(User).all()
    # Should be empty in isolated test database
    assert len(users) == 0

def test_sample_fixtures_work(sample_doctor, sample_nurse, sample_pharmacist):
    """Test that the sample fixtures are working correctly."""
    assert sample_doctor.role.value == "doctor"
    assert sample_nurse.role.value == "nurse"
    assert sample_pharmacist.role.value == "pharmacist"
    
    assert sample_doctor.api_key == "doctor_api_key_123"
    assert sample_nurse.api_key == "nurse_api_key_456"
    assert sample_pharmacist.api_key == "pharmacist_api_key_789" 