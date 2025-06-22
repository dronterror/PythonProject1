import pytest
import uuid
from fastapi.testclient import TestClient
from models import User, UserRole, Drug
from schemas import DrugCreate

class TestDrugStockTransferEndpoints:
    """Test the drug stock transfer feature using TDD approach."""
    
    # ============================================================================
    # 1. AUTHORIZATION & SECURITY TESTS
    # ============================================================================
    
    def test_transfer_drug_as_pharmacist_succeeds(self, client, test_user_pharmacist):
        """Verify a pharmacist can successfully transfer drug stock."""
        from dependencies import get_current_user
        from main import app
        app.dependency_overrides[get_current_user] = lambda: test_user_pharmacist
        
        # Create a drug with sufficient stock
        from crud import create_drug
        from schemas import DrugCreate
        from database import get_db
        db = next(get_db())
        
        drug_data = DrugCreate(
            name=f"Transfer Test Drug Success {uuid.uuid4()}",
            form="Tablet",
            strength="500mg",
            current_stock=100,
            low_stock_threshold=10
        )
        drug = create_drug(db, drug_data)
        
        # Perform transfer
        transfer_data = {
            "drug_id": str(drug.id),
            "source_ward": "ICU",
            "destination_ward": "Emergency",
            "quantity": 20
        }
        
        response = client.post("/api/drugs/transfer", json=transfer_data)
        assert response.status_code == 200
        
        # Verify response structure
        data = response.json()
        assert "id" in data
        assert data["drug_id"] == str(drug.id)
        assert data["source_ward"] == "ICU"
        assert data["destination_ward"] == "Emergency"
        assert data["quantity"] == 20
        assert "transfer_date" in data
        
        app.dependency_overrides.clear()
    
    def test_transfer_drug_as_doctor_is_forbidden(self, client, test_user_doctor):
        """Verify a doctor cannot transfer drug stock."""
        from dependencies import get_current_user
        from main import app
        app.dependency_overrides[get_current_user] = lambda: test_user_doctor
        
        transfer_data = {
            "drug_id": str(uuid.uuid4()),
            "source_ward": "ICU",
            "destination_ward": "Emergency",
            "quantity": 20
        }
        
        response = client.post("/api/drugs/transfer", json=transfer_data)
        assert response.status_code == 403
        assert "Insufficient permissions" in response.json()["detail"]
        
        app.dependency_overrides.clear()
    
    def test_transfer_drug_as_nurse_is_forbidden(self, client, test_user_nurse):
        """Verify a nurse cannot transfer drug stock."""
        from dependencies import get_current_user
        from main import app
        app.dependency_overrides[get_current_user] = lambda: test_user_nurse
        
        transfer_data = {
            "drug_id": str(uuid.uuid4()),
            "source_ward": "ICU",
            "destination_ward": "Emergency",
            "quantity": 20
        }
        
        response = client.post("/api/drugs/transfer", json=transfer_data)
        assert response.status_code == 403
        assert "Insufficient permissions" in response.json()["detail"]
        
        app.dependency_overrides.clear()
    
    def test_transfer_drug_with_no_authentication_is_unauthorized(self, client):
        """Verify transfer without API key returns 401."""
        transfer_data = {
            "drug_id": str(uuid.uuid4()),
            "source_ward": "ICU",
            "destination_ward": "Emergency",
            "quantity": 20
        }
        
        response = client.post("/api/drugs/transfer", json=transfer_data)
        assert response.status_code == 401
    
    def test_transfer_drug_with_invalid_authentication_is_unauthorized(self, client):
        """Verify transfer with fake API key returns 401."""
        transfer_data = {
            "drug_id": str(uuid.uuid4()),
            "source_ward": "ICU",
            "destination_ward": "Emergency",
            "quantity": 20
        }
        
        response = client.post(
            "/api/drugs/transfer", 
            json=transfer_data,
            headers={"X-API-Key": "fake-api-key"}
        )
        assert response.status_code == 401
    
    # ============================================================================
    # 2. INPUT VALIDATION TESTS (Pydantic Layer)
    # ============================================================================
    
    @pytest.mark.parametrize("field_name,invalid_value,expected_error", [
        ("drug_id", "not-a-uuid", "Input should be a valid UUID"),
        ("drug_id", "", "Input should be a valid UUID"),
        ("source_ward", "", "String should have at least 1 character"),
        ("source_ward", "a" * 200, "String should have at most 100 characters"),
        ("destination_ward", "", "String should have at least 1 character"),
        ("destination_ward", "a" * 200, "String should have at most 100 characters"),
        ("quantity", -1, "Input should be greater than 0"),
        ("quantity", 0, "Input should be greater than 0"),
        ("quantity", "not-a-number", "Input should be a valid integer"),
        ("quantity", 1.5, "Input should be a valid integer"),
    ])
    def test_transfer_drug_with_invalid_input_validation(self, client, test_user_pharmacist, field_name, invalid_value, expected_error):
        """Test input validation for all fields using parameterized tests."""
        from dependencies import get_current_user
        from main import app
        app.dependency_overrides[get_current_user] = lambda: test_user_pharmacist
        
        transfer_data = {
            "drug_id": str(uuid.uuid4()),
            "source_ward": "ICU",
            "destination_ward": "Emergency",
            "quantity": 20
        }
        
        # Replace the field with invalid value
        transfer_data[field_name] = invalid_value
        
        response = client.post("/api/drugs/transfer", json=transfer_data)
        assert response.status_code == 422
        
        # Check that the error message contains the expected validation error
        error_detail = response.json()["detail"]
        assert any(expected_error in str(error) for error in error_detail)
        
        app.dependency_overrides.clear()
    
    # ============================================================================
    # 3. BUSINESS LOGIC & EDGE CASE TESTS
    # ============================================================================
    
    def test_transfer_drug_with_valid_data_works_correctly(self, client, test_user_pharmacist):
        """Test the happy path - successful transfer with database verification."""
        from dependencies import get_current_user
        from main import app
        app.dependency_overrides[get_current_user] = lambda: test_user_pharmacist
        
        # Create a drug with sufficient stock
        from crud import create_drug
        from schemas import DrugCreate
        from database import get_db
        db = next(get_db())
        
        drug_data = DrugCreate(
            name=f"Transfer Test Drug Valid Data {uuid.uuid4()}",
            form="Tablet",
            strength="500mg",
            current_stock=100,
            low_stock_threshold=10
        )
        drug = create_drug(db, drug_data)
        
        # Verify initial stock
        assert drug.current_stock == 100
        
        # Perform transfer
        transfer_data = {
            "drug_id": str(drug.id),
            "source_ward": "ICU",
            "destination_ward": "Emergency",
            "quantity": 30
        }
        
        response = client.post("/api/drugs/transfer", json=transfer_data)
        assert response.status_code == 200
        
        # Verify response
        data = response.json()
        assert data["drug_id"] == str(drug.id)
        assert data["source_ward"] == "ICU"
        assert data["destination_ward"] == "Emergency"
        assert data["quantity"] == 30
        
        # Verify database changes
        db.refresh(drug)
        assert drug.current_stock == 70  # 100 - 30
        
        app.dependency_overrides.clear()
    
    def test_transfer_drug_when_drug_not_found_fails(self, client, test_user_pharmacist):
        """Test transfer with non-existent drug ID."""
        from dependencies import get_current_user
        from main import app
        app.dependency_overrides[get_current_user] = lambda: test_user_pharmacist
        
        transfer_data = {
            "drug_id": str(uuid.uuid4()),  # Non-existent drug
            "source_ward": "ICU",
            "destination_ward": "Emergency",
            "quantity": 20
        }
        
        response = client.post("/api/drugs/transfer", json=transfer_data)
        assert response.status_code == 404
        assert "Drug not found" in response.json()["detail"]
        
        app.dependency_overrides.clear()
    
    def test_transfer_drug_when_insufficient_stock_fails(self, client, test_user_pharmacist):
        """Test transfer when source ward has insufficient stock."""
        from dependencies import get_current_user
        from main import app
        app.dependency_overrides[get_current_user] = lambda: test_user_pharmacist
        
        # Create a drug with low stock
        from crud import create_drug
        from schemas import DrugCreate
        from database import get_db
        db = next(get_db())
        
        drug_data = DrugCreate(
            name=f"Low Stock Drug Transfer Test {uuid.uuid4()}",
            form="Tablet",
            strength="500mg",
            current_stock=10,
            low_stock_threshold=5
        )
        drug = create_drug(db, drug_data)
        
        # Try to transfer more than available
        transfer_data = {
            "drug_id": str(drug.id),
            "source_ward": "ICU",
            "destination_ward": "Emergency",
            "quantity": 20  # More than available stock
        }
        
        response = client.post("/api/drugs/transfer", json=transfer_data)
        assert response.status_code == 400
        assert "Insufficient stock" in response.json()["detail"]
        
        # Verify no changes were made to the database
        db.refresh(drug)
        assert drug.current_stock == 10  # Unchanged
        
        app.dependency_overrides.clear()
    
    def test_transfer_drug_when_same_ward_fails(self, client, test_user_pharmacist):
        """Test transfer when source and destination wards are the same."""
        from dependencies import get_current_user
        from main import app
        app.dependency_overrides[get_current_user] = lambda: test_user_pharmacist
        
        # Create a drug
        from crud import create_drug
        from schemas import DrugCreate
        from database import get_db
        db = next(get_db())
        
        drug_data = DrugCreate(
            name=f"Same Ward Drug Transfer Test {uuid.uuid4()}",
            form="Tablet",
            strength="500mg",
            current_stock=100,
            low_stock_threshold=10
        )
        drug = create_drug(db, drug_data)
        
        # Try to transfer to same ward
        transfer_data = {
            "drug_id": str(drug.id),
            "source_ward": "ICU",
            "destination_ward": "ICU",  # Same as source
            "quantity": 20
        }
        
        response = client.post("/api/drugs/transfer", json=transfer_data)
        assert response.status_code == 400
        assert "Source and destination wards must be different" in response.json()["detail"]
        
        # Verify no changes were made to the database
        db.refresh(drug)
        assert drug.current_stock == 100  # Unchanged
        
        app.dependency_overrides.clear()
    
    def test_transfer_drug_when_zero_quantity_fails(self, client, test_user_pharmacist):
        """Test transfer with zero quantity."""
        from dependencies import get_current_user
        from main import app
        app.dependency_overrides[get_current_user] = lambda: test_user_pharmacist
        
        # Create a drug
        from crud import create_drug
        from schemas import DrugCreate
        from database import get_db
        db = next(get_db())
        
        drug_data = DrugCreate(
            name=f"Zero Quantity Drug Transfer Test {uuid.uuid4()}",
            form="Tablet",
            strength="500mg",
            current_stock=100,
            low_stock_threshold=10
        )
        drug = create_drug(db, drug_data)
        
        # Try to transfer zero quantity
        transfer_data = {
            "drug_id": str(drug.id),
            "source_ward": "ICU",
            "destination_ward": "Emergency",
            "quantity": 0
        }
        
        response = client.post("/api/drugs/transfer", json=transfer_data)
        assert response.status_code == 422  # Validation error
        
        app.dependency_overrides.clear()
    
    def test_transfer_drug_creates_transfer_record(self, client, test_user_pharmacist):
        """Test that a transfer record is created in the database."""
        from dependencies import get_current_user
        from main import app
        app.dependency_overrides[get_current_user] = lambda: test_user_pharmacist
        
        # Create a drug
        from crud import create_drug
        from schemas import DrugCreate
        from database import get_db
        db = next(get_db())
        
        drug_data = DrugCreate(
            name=f"Transfer Record Drug Test {uuid.uuid4()}",
            form="Tablet",
            strength="500mg",
            current_stock=100,
            low_stock_threshold=10
        )
        drug = create_drug(db, drug_data)
        
        # Perform transfer
        transfer_data = {
            "drug_id": str(drug.id),
            "source_ward": "ICU",
            "destination_ward": "Emergency",
            "quantity": 25
        }
        
        response = client.post("/api/drugs/transfer", json=transfer_data)
        assert response.status_code == 200
        
        # Verify transfer record was created
        from models import DrugTransfer
        transfer_record = db.query(DrugTransfer).filter(
            DrugTransfer.drug_id == drug.id,
            DrugTransfer.source_ward == "ICU",
            DrugTransfer.destination_ward == "Emergency",
            DrugTransfer.quantity == 25
        ).first()
        
        assert transfer_record is not None
        assert transfer_record.pharmacist_id == test_user_pharmacist.id
        
        app.dependency_overrides.clear() 