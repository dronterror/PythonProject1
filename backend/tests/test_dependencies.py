import pytest
from fastapi import HTTPException
from dependencies import get_current_user, require_role, require_roles
from models import User, UserRole

class TestDependencies:
    def test_get_current_user_valid_api_key(self, db_session, test_user_doctor):
        """Test getting current user with valid API key."""
        # Mock the API key header
        api_key = test_user_doctor.api_key
        
        # Test the dependency
        user = get_current_user(api_key=api_key, db=db_session)
        
        assert user is not None
        assert user.id == test_user_doctor.id
        assert user.email == test_user_doctor.email
        assert user.role == test_user_doctor.role
    
    def test_get_current_user_invalid_api_key(self, db_session):
        """Test getting current user with invalid API key."""
        api_key = "invalid_api_key"
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(api_key=api_key, db=db_session)
        
        assert exc_info.value.status_code == 401
        assert "Invalid API Key" in str(exc_info.value.detail)
    
    def test_get_current_user_missing_api_key(self, db_session):
        """Test getting current user with missing API key."""
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(api_key=None, db=db_session)
        
        assert exc_info.value.status_code == 401
        assert "Missing API Key" in str(exc_info.value.detail)
    
    def test_require_role_doctor_access(self, db_session, test_user_doctor):
        """Test role requirement for doctor access."""
        doctor_dependency = require_role("doctor")
        user = test_user_doctor
        result = doctor_dependency(current_user=user)
        assert result == user
    
    def test_require_role_doctor_denied(self, db_session, test_user_nurse):
        """Test role requirement denies non-doctor access."""
        doctor_dependency = require_role("doctor")
        user = test_user_nurse
        with pytest.raises(HTTPException) as exc_info:
            doctor_dependency(current_user=user)
        assert exc_info.value.status_code == 403
        assert "Insufficient permissions" in str(exc_info.value.detail)
    
    def test_require_role_nurse_access(self, db_session, test_user_nurse):
        """Test role requirement for nurse access."""
        nurse_dependency = require_role("nurse")
        user = test_user_nurse
        result = nurse_dependency(current_user=user)
        assert result == user
    
    def test_require_role_pharmacist_access(self, db_session, test_user_pharmacist):
        """Test role requirement for pharmacist access."""
        pharmacist_dependency = require_role("pharmacist")
        user = test_user_pharmacist
        result = pharmacist_dependency(current_user=user)
        assert result == user
    
    def test_require_role_invalid_role(self, db_session, test_user_doctor):
        """Test role requirement with invalid role."""
        invalid_dependency = require_role("invalid_role")
        user = test_user_doctor
        with pytest.raises(HTTPException) as exc_info:
            invalid_dependency(current_user=user)
        assert exc_info.value.status_code == 403
        assert "Insufficient permissions" in str(exc_info.value.detail)
    
    def test_require_role_missing_user(self, db_session):
        """Test role requirement with missing user."""
        doctor_dependency = require_role("doctor")
        user = None
        with pytest.raises(AttributeError):
            doctor_dependency(current_user=user)
    
    # Tests for new require_roles function
    def test_require_roles_nurse_access(self, db_session, test_user_nurse):
        """Test require_roles allows nurse access when nurse is in allowed list."""
        nurse_pharmacist_dependency = require_roles(["nurse", "pharmacist"])
        user = test_user_nurse
        result = nurse_pharmacist_dependency(current_user=user)
        assert result == user
    
    def test_require_roles_pharmacist_access(self, db_session, test_user_pharmacist):
        """Test require_roles allows pharmacist access when pharmacist is in allowed list."""
        nurse_pharmacist_dependency = require_roles(["nurse", "pharmacist"])
        user = test_user_pharmacist
        result = nurse_pharmacist_dependency(current_user=user)
        assert result == user
    
    def test_require_roles_doctor_denied(self, db_session, test_user_doctor):
        """Test require_roles denies doctor access when doctor is not in allowed list."""
        nurse_pharmacist_dependency = require_roles(["nurse", "pharmacist"])
        user = test_user_doctor
        with pytest.raises(HTTPException) as exc_info:
            nurse_pharmacist_dependency(current_user=user)
        assert exc_info.value.status_code == 403
        assert "Access denied" in str(exc_info.value.detail)
        assert "nurse, pharmacist" in str(exc_info.value.detail)
    
    def test_require_roles_single_role(self, db_session, test_user_doctor):
        """Test require_roles works with a single role."""
        doctor_only_dependency = require_roles(["doctor"])
        user = test_user_doctor
        result = doctor_only_dependency(current_user=user)
        assert result == user
    
    def test_require_roles_empty_list(self, db_session, test_user_doctor):
        """Test require_roles denies access when allowed_roles is empty."""
        empty_dependency = require_roles([])
        user = test_user_doctor
        with pytest.raises(HTTPException) as exc_info:
            empty_dependency(current_user=user)
        assert exc_info.value.status_code == 403
        assert "Access denied" in str(exc_info.value.detail) 