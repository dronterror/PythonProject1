import pytest
from fastapi.testclient import TestClient
from main import app
from models import User, UserRole
import uuid

class TestSmartPrescribingEndpoints:
    """Test the new Smart Prescribing endpoints for doctors."""
    
    def test_get_formulary_doctor_access(self, client, test_user_doctor):
        """Test that doctors can access the formulary endpoint."""
        from dependencies import get_current_user
        from main import app
        app.dependency_overrides[get_current_user] = lambda: test_user_doctor
        
        # Create a drug first
        from crud import create_drug
        from schemas import DrugCreate
        from database import get_db
        db = next(get_db())
        
        drug_data = DrugCreate(
            name="Test Drug for Formulary",
            form="Tablet",
            strength="500mg",
            current_stock=100,
            low_stock_threshold=10
        )
        create_drug(db, drug_data)
        
        # Test formulary endpoint
        response = client.get("/api/drugs/formulary")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert "id" in data[0]
        assert "name" in data[0]
        assert "form" in data[0]
        assert "strength" in data[0]
        
        app.dependency_overrides.clear()
    
    def test_get_inventory_status_doctor_access(self, client, test_user_doctor):
        """Test that doctors can access the inventory status endpoint."""
        from dependencies import get_current_user
        from main import app
        app.dependency_overrides[get_current_user] = lambda: test_user_doctor
        
        # Create a drug first
        from crud import create_drug
        from schemas import DrugCreate
        from database import get_db
        db = next(get_db())
        
        drug_data = DrugCreate(
            name="Test Drug for Inventory",
            form="Tablet",
            strength="500mg",
            current_stock=5,  # Low stock
            low_stock_threshold=10
        )
        drug = create_drug(db, drug_data)
        
        # Test inventory status endpoint
        response = client.get("/api/drugs/inventory/status")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert str(drug.id) in data
        assert "stock" in data[str(drug.id)]
        assert "status" in data[str(drug.id)]
        assert data[str(drug.id)]["status"] == "low_stock"
        
        app.dependency_overrides.clear()
    
    def test_formulary_unauthorized_access(self, client, test_user_nurse):
        """Test that non-doctors cannot access the formulary endpoint."""
        from dependencies import get_current_user
        from main import app
        app.dependency_overrides[get_current_user] = lambda: test_user_nurse
        
        response = client.get("/api/drugs/formulary")
        assert response.status_code == 403
        
        app.dependency_overrides.clear()
    
    def test_inventory_status_unauthorized_access(self, client, test_user_nurse):
        """Test that non-doctors cannot access the inventory status endpoint."""
        from dependencies import get_current_user
        from main import app
        app.dependency_overrides[get_current_user] = lambda: test_user_nurse
        
        response = client.get("/api/drugs/inventory/status")
        assert response.status_code == 403
        
        app.dependency_overrides.clear()

class TestEfficientNurseWorkflowEndpoints:
    """Test the new Efficient Nurse Workflow endpoints."""
    
    def test_bulk_administration_nurse_access(self, client, test_user_nurse):
        """Test that nurses can access the bulk administration endpoint."""
        from dependencies import get_current_user
        from main import app
        app.dependency_overrides[get_current_user] = lambda: test_user_nurse
        
        # Create a drug and order first
        from crud import create_drug, create_with_doctor
        from schemas import DrugCreate, MedicationOrderCreate
        from database import get_db
        db = next(get_db())
        
        # Create drug
        drug_data = DrugCreate(
            name="Test Drug for Bulk Admin",
            form="Tablet",
            strength="500mg",
            current_stock=10,
            low_stock_threshold=5
        )
        drug = create_drug(db, drug_data)
        
        # Create order
        order_data = MedicationOrderCreate(
            patient_name="Test Patient",
            drug_id=drug.id,
            dosage=2,
            schedule="BID"
        )
        order = create_with_doctor(db, order_data, test_user_nurse.id)
        
        # Test bulk administration endpoint
        response = client.post("/api/administrations/bulk", json=[str(order.id)])
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        
        app.dependency_overrides.clear()
    
    def test_mar_dashboard_nurse_access(self, client, test_user_nurse):
        """Test that nurses can access the MAR dashboard endpoint."""
        from dependencies import get_current_user
        from main import app
        app.dependency_overrides[get_current_user] = lambda: test_user_nurse
        
        # Create a drug and order first
        from crud import create_drug, create_with_doctor
        from schemas import DrugCreate, MedicationOrderCreate
        from database import get_db
        db = next(get_db())
        
        # Create drug
        drug_data = DrugCreate(
            name="Test Drug for Dashboard",
            form="Tablet",
            strength="500mg",
            current_stock=10,
            low_stock_threshold=5
        )
        drug = create_drug(db, drug_data)
        
        # Create order
        order_data = MedicationOrderCreate(
            patient_name="Test Patient",
            drug_id=drug.id,
            dosage=2,
            schedule="BID"
        )
        create_with_doctor(db, order_data, test_user_nurse.id)
        
        # Test MAR dashboard endpoint
        response = client.get("/api/orders/mar-dashboard")
        assert response.status_code == 200
        data = response.json()
        assert "patients" in data
        assert "summary" in data
        assert isinstance(data["patients"], list)
        assert isinstance(data["summary"], dict)
        
        app.dependency_overrides.clear()
    
    def test_bulk_administration_unauthorized_access(self, client, test_user_doctor):
        """Test that non-nurses cannot access the bulk administration endpoint."""
        from dependencies import get_current_user
        from main import app
        app.dependency_overrides[get_current_user] = lambda: test_user_doctor
        
        response = client.post("/api/administrations/bulk", json=[])
        assert response.status_code == 403
        
        app.dependency_overrides.clear()
    
    def test_mar_dashboard_unauthorized_access(self, client, test_user_doctor):
        """Test that non-nurses cannot access the MAR dashboard endpoint."""
        from dependencies import get_current_user
        from main import app
        app.dependency_overrides[get_current_user] = lambda: test_user_doctor
        
        response = client.get("/api/orders/mar-dashboard")
        assert response.status_code == 403
        
        app.dependency_overrides.clear() 