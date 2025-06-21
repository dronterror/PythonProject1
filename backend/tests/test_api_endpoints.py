import pytest
from fastapi.testclient import TestClient
from datetime import datetime

# --- Health Endpoints ---
class TestHealthEndpoints:
    def test_root_endpoint(self, client):
        """Test the root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        assert "Medication Logistics MVP Backend" in response.json()["message"]
    
    def test_health_check(self, client):
        """Test the health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

# --- Drugs Endpoints ---
class TestDrugsEndpoints:
    def test_create_drug_pharmacist_access(self, client, test_user_pharmacist):
        """Test creating a drug with pharmacist access."""
        # Override get_current_user for this test
        from dependencies import get_current_user
        from main import app
        app.dependency_overrides[get_current_user] = lambda: test_user_pharmacist
        
        drug_name = f"Unique Test Drug {datetime.now().timestamp()}"
        drug_data = {
            "name": drug_name,
            "form": "Tablet",
            "strength": "500mg",
            "current_stock": 100,
            "low_stock_threshold": 10
        }
        
        response = client.post(
            "/api/drugs/",
            json=drug_data,
        )

        if response.status_code != 200:
            print(f"Drug creation failed with status {response.status_code}: {response.json()}")
            
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == drug_name
        
        # Clean up override
        app.dependency_overrides.clear()
    
    @pytest.mark.usefixtures("test_drug")
    def test_create_drug_duplicate(self, client, test_user_pharmacist, test_drug):
        """Test creating a duplicate drug."""
        # Override get_current_user for this test
        from dependencies import get_current_user
        from main import app
        app.dependency_overrides[get_current_user] = lambda: test_user_pharmacist
        
        drug_data = {
            "name": test_drug.name,
            "form": test_drug.form,
            "strength": test_drug.strength,
            "current_stock": 50,
            "low_stock_threshold": 5
        }
        
        response = client.post(
            "/api/drugs/",
            json=drug_data,
        )
        
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]
        
        # Clean up override
        app.dependency_overrides.clear()
    
    def test_create_drug_unauthorized(self, client, test_user_doctor):
        """Test creating a drug without pharmacist access."""
        # Override get_current_user for this test
        from dependencies import get_current_user
        from main import app
        app.dependency_overrides[get_current_user] = lambda: test_user_doctor
        
        drug_data = {
            "name": "Test Drug",
            "form": "Tablet",
            "strength": "500mg",
            "current_stock": 100,
            "low_stock_threshold": 10
        }
        
        response = client.post(
            "/api/drugs/",
            json=drug_data,
        )
        
        assert response.status_code == 403
        
        # Clean up override
        app.dependency_overrides.clear()
    
    @pytest.mark.usefixtures("test_drug")
    def test_update_drug(self, client, test_user_pharmacist, test_drug):
        """Test updating a drug."""
        # Override get_current_user for this test
        from dependencies import get_current_user
        from main import app
        app.dependency_overrides[get_current_user] = lambda: test_user_pharmacist
        
        update_data = {
            "current_stock": 75,
            "low_stock_threshold": 15
        }
        
        response = client.put(
            f"/api/drugs/{test_drug.id}",
            json=update_data,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["current_stock"] == 75
        assert data["low_stock_threshold"] == 15
        
        # Clean up override
        app.dependency_overrides.clear()
    
    def test_update_drug_not_found(self, client, test_user_pharmacist):
        """Test updating a non-existent drug."""
        # Override get_current_user for this test
        from dependencies import get_current_user
        from main import app
        app.dependency_overrides[get_current_user] = lambda: test_user_pharmacist
        
        update_data = {"current_stock": 75}
        
        response = client.put(
            "/api/drugs/999",
            json=update_data,
        )
        
        assert response.status_code == 404
        
        # Clean up override
        app.dependency_overrides.clear()
    
    @pytest.mark.usefixtures("test_drug")
    def test_get_low_stock_drugs(self, client, test_user_pharmacist, test_drug):
        """Test getting low stock drugs."""
        # Override get_current_user for this test
        from dependencies import get_current_user
        from main import app
        app.dependency_overrides[get_current_user] = lambda: test_user_pharmacist
        
        # Update drug to be low stock
        test_drug.current_stock = 5
        client.put(
            f"/api/drugs/{test_drug.id}",
            json={"current_stock": 5},
        )
        
        response = client.get("/api/drugs/low-stock")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(drug["id"] == test_drug.id for drug in data)
        
        # Clean up override
        app.dependency_overrides.clear()
    
    @pytest.mark.usefixtures("test_drug")
    def test_get_drugs(self, client, test_user_doctor, test_drug):
        """Test getting all drugs."""
        # Override get_current_user for this test
        from dependencies import get_current_user
        from main import app
        app.dependency_overrides[get_current_user] = lambda: test_user_doctor
        
        response = client.get("/api/drugs/")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(drug["id"] == test_drug.id for drug in data)
        
        # Clean up override
        app.dependency_overrides.clear()

# --- Orders Endpoints ---
class TestOrdersEndpoints:
    @pytest.mark.usefixtures("test_drug")
    def test_create_order_doctor_access(self, client, test_user_doctor, test_drug):
        """Test creating an order with doctor access."""
        # Override get_current_user for this test
        from dependencies import get_current_user
        from main import app
        app.dependency_overrides[get_current_user] = lambda: test_user_doctor
        
        order_data = {
            "patient_name": "John Doe",
            "drug_id": test_drug.id,
            "dosage": 2,
            "schedule": "Every 8 hours"
        }
        
        response = client.post(
            "/api/orders/",
            json=order_data,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["patient_name"] == "John Doe"
        assert data["drug_id"] == test_drug.id
        assert data["dosage"] == 2
        assert data["status"] == "active"
        
        # Clean up override
        app.dependency_overrides.clear()
    
    def test_create_order_drug_not_found(self, client, test_user_doctor):
        """Test creating an order with non-existent drug."""
        # Override get_current_user for this test
        from dependencies import get_current_user
        from main import app
        app.dependency_overrides[get_current_user] = lambda: test_user_doctor
        
        order_data = {
            "patient_name": "John Doe",
            "drug_id": 999,
            "dosage": 2,
            "schedule": "Every 8 hours"
        }
        
        response = client.post(
            "/api/orders/",
            json=order_data,
        )
        
        assert response.status_code == 404
        assert "Drug not found" in response.json()["detail"]
        
        # Clean up override
        app.dependency_overrides.clear()
    
    @pytest.mark.usefixtures("test_drug")
    def test_create_order_unauthorized(self, client, test_user_nurse, test_drug):
        """Test creating an order without doctor access."""
        # Override get_current_user for this test
        from dependencies import get_current_user
        from main import app
        app.dependency_overrides[get_current_user] = lambda: test_user_nurse
        
        order_data = {
            "patient_name": "John Doe",
            "drug_id": test_drug.id,
            "dosage": 2,
            "schedule": "Every 8 hours"
        }
        
        response = client.post(
            "/api/orders/",
            json=order_data,
        )
        
        assert response.status_code == 403
        
        # Clean up override
        app.dependency_overrides.clear()
    
    @pytest.mark.usefixtures("test_order")
    def test_get_orders(self, client, test_user_doctor, test_order):
        """Test getting all orders."""
        # Override get_current_user for this test
        from dependencies import get_current_user
        from main import app
        app.dependency_overrides[get_current_user] = lambda: test_user_doctor
        
        response = client.get("/api/orders/")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(order["id"] == test_order.id for order in data)
        
        # Clean up override
        app.dependency_overrides.clear()
    
    @pytest.mark.usefixtures("test_order")
    def test_get_orders_by_status(self, client, test_user_doctor, test_order):
        """Test getting orders by status."""
        # Override get_current_user for this test
        from dependencies import get_current_user
        from main import app
        app.dependency_overrides[get_current_user] = lambda: test_user_doctor
        
        response = client.get(
            "/api/orders/",
            params={"status": "active"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert all(order["status"] == "active" for order in data)
        
        # Clean up override
        app.dependency_overrides.clear()
    
    # Tests for new collaborative endpoints
    @pytest.mark.usefixtures("test_order")
    def test_get_my_orders_doctor_access(self, client, test_user_doctor, test_order):
        """Test doctor can access their own orders."""
        # Override get_current_user for this test
        from dependencies import get_current_user
        from main import app
        app.dependency_overrides[get_current_user] = lambda: test_user_doctor
        
        response = client.get("/api/orders/my-orders/")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(order["id"] == test_order.id for order in data)
        assert all(order["doctor_id"] == test_user_doctor.id for order in data)
        
        # Clean up override
        app.dependency_overrides.clear()
    
    def test_get_my_orders_nurse_denied(self, client, test_user_nurse):
        """Test nurse cannot access doctor's my-orders endpoint."""
        # Override get_current_user for this test
        from dependencies import get_current_user
        from main import app
        app.dependency_overrides[get_current_user] = lambda: test_user_nurse
        
        response = client.get("/api/orders/my-orders/")
        
        assert response.status_code == 403
        
        # Clean up override
        app.dependency_overrides.clear()
    
    @pytest.mark.usefixtures("test_order")
    def test_get_active_mar_nurse_access(self, client, test_user_nurse, test_order):
        """Test nurse can access active MAR endpoint."""
        # Override get_current_user for this test
        from dependencies import get_current_user
        from main import app
        app.dependency_overrides[get_current_user] = lambda: test_user_nurse
        
        response = client.get("/api/orders/active-mar/")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(order["id"] == test_order.id for order in data)
        assert all(order["status"] == "active" for order in data)
        
        # Clean up override
        app.dependency_overrides.clear()
    
    @pytest.mark.usefixtures("test_order")
    def test_get_active_mar_pharmacist_access(self, client, test_user_pharmacist, test_order):
        """Test pharmacist can access active MAR endpoint."""
        # Override get_current_user for this test
        from dependencies import get_current_user
        from main import app
        app.dependency_overrides[get_current_user] = lambda: test_user_pharmacist
        
        response = client.get("/api/orders/active-mar/")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(order["id"] == test_order.id for order in data)
        assert all(order["status"] == "active" for order in data)
        
        # Clean up override
        app.dependency_overrides.clear()
    
    def test_get_active_mar_doctor_denied(self, client, test_user_doctor):
        """Test doctor cannot access active MAR endpoint."""
        # Override get_current_user for this test
        from dependencies import get_current_user
        from main import app
        app.dependency_overrides[get_current_user] = lambda: test_user_doctor
        
        response = client.get("/api/orders/active-mar/")
        
        assert response.status_code == 403
        
        # Clean up override
        app.dependency_overrides.clear()

# --- Administrations Endpoints ---
class TestAdministrationsEndpoints:
    @pytest.mark.usefixtures("test_order")
    def test_create_administration_nurse_access(self, client, db_session, test_user_nurse, test_order):
        """Test creating an administration with nurse access."""
        # Override get_current_user and get_db for this test
        from dependencies import get_current_user, get_db
        from main import app
        app.dependency_overrides[get_current_user] = lambda: test_user_nurse
        app.dependency_overrides[get_db] = lambda: db_session

        # Ensure the drug exists in the test database
        from models import Drug
        drug = Drug(
            name="Test Drug for Administration",
            form="Tablet",
            strength="100mg",
            current_stock=10,
            low_stock_threshold=5
        )
        db_session.add(drug)
        db_session.commit()
        db_session.refresh(drug)

        # Update the test order to use this drug
        test_order.drug_id = drug.id
        db_session.add(test_order)
        db_session.commit()

        admin_data = {
            "order_id": test_order.id,
            "nurse_id": test_user_nurse.id
        }

        response = client.post(
            "/api/administrations/",
            json=admin_data,
        )

        if response.status_code != 200:
            print(f"Administration creation failed with status {response.status_code}: {response.json()}")
            
        assert response.status_code == 200
        data = response.json()
        assert data["order_id"] == test_order.id
        assert data["nurse_id"] == test_user_nurse.id
        
        # Clean up override
        app.dependency_overrides.clear()
    
    def test_create_administration_order_not_found(self, client, db_session, test_user_nurse):
        """Test creating an administration with non-existent order."""
        # Override get_current_user and get_db for this test
        from dependencies import get_current_user, get_db
        from main import app
        app.dependency_overrides[get_current_user] = lambda: test_user_nurse
        app.dependency_overrides[get_db] = lambda: db_session

        admin_data = {
            "order_id": 999,
            "nurse_id": test_user_nurse.id
        }

        response = client.post(
            "/api/administrations/",
            json=admin_data,
        )

        if response.status_code != 404:
            print(f"Administration creation failed with status {response.status_code}: {response.json()}")
            
        assert response.status_code == 404
        assert "Order not found" in response.json()["detail"]
        
        # Clean up override
        app.dependency_overrides.clear()
    
    @pytest.mark.usefixtures("test_order")
    def test_create_administration_unauthorized(self, client, test_user_doctor, test_order):
        """Test creating an administration without nurse access."""
        # Override get_current_user for this test
        from dependencies import get_current_user
        from main import app
        app.dependency_overrides[get_current_user] = lambda: test_user_doctor

        admin_data = {
            "order_id": test_order.id,
            "nurse_id": test_user_doctor.id
        }

        response = client.post(
            "/api/administrations/",
            json=admin_data,
        )

        assert response.status_code == 403
        
        # Clean up override
        app.dependency_overrides.clear()
    
    @pytest.mark.usefixtures("test_order")
    def test_get_administrations(self, client, db_session, test_user_nurse, test_order):
        """Test getting all administrations."""
        # Override get_current_user and get_db for this test
        from dependencies import get_current_user, get_db
        from main import app
        app.dependency_overrides[get_current_user] = lambda: test_user_nurse
        app.dependency_overrides[get_db] = lambda: db_session

        # Ensure the drug exists in the test database
        from models import Drug
        drug = Drug(
            name="Test Drug for Get Administrations",
            form="Tablet",
            strength="200mg",
            current_stock=10,
            low_stock_threshold=5
        )
        db_session.add(drug)
        db_session.commit()
        db_session.refresh(drug)

        # Update the test order to use this drug
        test_order.drug_id = drug.id
        db_session.add(test_order)
        db_session.commit()

        # First create an administration
        admin_data = {"order_id": test_order.id, "nurse_id": test_user_nurse.id}
        response = client.post(
            "/api/administrations/",
            json=admin_data,
        )

        if response.status_code != 200:
            print(f"Administration creation failed with status {response.status_code}: {response.json()}")

        response = client.get("/api/administrations/")

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(admin["order_id"] == test_order.id for admin in data)
        
        # Clean up override
        app.dependency_overrides.clear()

# --- Authentication ---
class TestAuthentication:
    def test_missing_api_key(self, client):
        """Test endpoints without API key."""
        response = client.get("/api/drugs/")
        assert response.status_code == 401
    
    def test_invalid_api_key(self, client):
        """Test endpoints with invalid API key."""
        response = client.get(
            "/api/drugs/",
            headers={"X-API-Key": "invalid_key"}
        )
        assert response.status_code == 401 