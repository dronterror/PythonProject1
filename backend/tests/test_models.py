import pytest
from sqlalchemy.exc import IntegrityError
from models import User, UserRole, Drug, MedicationOrder, OrderStatus, MedicationAdministration
from datetime import datetime
from crud import get_multi_by_doctor

class TestUserModel:
    def test_create_user(self, db_session):
        """Test creating a user with valid data."""
        user = User(
            email="test@example.com",
            role=UserRole.doctor,
            api_key="test_api_key",
            hashed_password="hashed_password"
        )
        db_session.add(user)
        db_session.commit()
        
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.role == UserRole.doctor
        assert user.api_key == "test_api_key"
    
    def test_user_email_unique_constraint(self, db_session):
        """Test that email must be unique."""
        user1 = User(
            email="test@example.com",
            role=UserRole.doctor,
            api_key="key1",
            hashed_password="password"
        )
        db_session.add(user1)
        db_session.commit()
        
        user2 = User(
            email="test@example.com",  # Same email
            role=UserRole.nurse,
            api_key="key2",
            hashed_password="password"
        )
        db_session.add(user2)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_user_api_key_unique_constraint(self, db_session):
        """Test that API key must be unique."""
        user1 = User(
            email="test1@example.com",
            role=UserRole.doctor,
            api_key="same_key",
            hashed_password="password"
        )
        db_session.add(user1)
        db_session.commit()
        
        user2 = User(
            email="test2@example.com",
            role=UserRole.nurse,
            api_key="same_key",  # Same API key
            hashed_password="password"
        )
        db_session.add(user2)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_user_repr(self, db_session):
        """Test user string representation."""
        user = User(
            email="test@example.com",
            role=UserRole.pharmacist,
            api_key="test_key",
            hashed_password="password"
        )
        db_session.add(user)
        db_session.commit()
        
        assert "test@example.com" in str(user)
        assert "pharmacist" in str(user)

class TestDrugModel:
    def test_create_drug(self, db_session):
        """Test creating a drug with valid data."""
        drug = Drug(
            name="Aspirin",
            form="Tablet",
            strength="500mg",
            current_stock=50,
            low_stock_threshold=10
        )
        db_session.add(drug)
        db_session.commit()
        
        assert drug.id is not None
        assert drug.name == "Aspirin"
        assert drug.form == "Tablet"
        assert drug.strength == "500mg"
        assert drug.current_stock == 50
        assert drug.low_stock_threshold == 10
    
    def test_drug_unique_constraint(self, db_session):
        """Test that drug name+form+strength combination must be unique."""
        drug1 = Drug(
            name="Aspirin",
            form="Tablet",
            strength="500mg",
            current_stock=50,
            low_stock_threshold=10
        )
        db_session.add(drug1)
        db_session.commit()
        
        drug2 = Drug(
            name="Aspirin",  # Same name, form, strength
            form="Tablet",
            strength="500mg",
            current_stock=30,
            low_stock_threshold=5
        )
        db_session.add(drug2)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_drug_repr(self, db_session):
        """Test drug string representation."""
        drug = Drug(
            name="Aspirin",
            form="Tablet",
            strength="500mg",
            current_stock=50,
            low_stock_threshold=10
        )
        db_session.add(drug)
        db_session.commit()
        
        assert "Aspirin" in str(drug)
        assert "50" in str(drug)

class TestMedicationOrderModel:
    def test_create_order(self, db_session, test_user_doctor, test_drug):
        """Test creating a medication order."""
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
        
        assert order.id is not None
        assert order.patient_name == "John Doe"
        assert order.drug_id == test_drug.id
        assert order.dosage == 2
        assert order.schedule == "Every 8 hours"
        assert order.status == OrderStatus.active
        assert order.doctor_id == test_user_doctor.id
    
    def test_order_relationships(self, db_session, test_user_doctor, test_drug):
        """Test order relationships with drug and doctor."""
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
        
        # Test relationships
        assert order.drug == test_drug
        assert order.doctor == test_user_doctor
    
    def test_order_repr(self, db_session, test_user_doctor, test_drug):
        """Test order string representation."""
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
        
        assert "John Doe" in str(order)
        assert str(test_drug.id) in str(order)

class TestMedicationAdministrationModel:
    def test_create_administration(self, db_session, test_user_nurse, test_order):
        """Test creating a medication administration."""
        admin = MedicationAdministration(
            order_id=test_order.id,
            nurse_id=test_user_nurse.id
        )
        db_session.add(admin)
        db_session.commit()
        
        assert admin.id is not None
        assert admin.order_id == test_order.id
        assert admin.nurse_id == test_user_nurse.id
        assert admin.administration_time is not None
    
    def test_administration_relationships(self, db_session, test_user_nurse, test_order):
        """Test administration relationships."""
        admin = MedicationAdministration(
            order_id=test_order.id,
            nurse_id=test_user_nurse.id
        )
        db_session.add(admin)
        db_session.commit()
        
        assert admin.order == test_order
        assert admin.nurse == test_user_nurse
    
    def test_administration_repr(self, db_session, test_user_nurse, test_order):
        """Test administration string representation."""
        admin = MedicationAdministration(
            order_id=test_order.id,
            nurse_id=test_user_nurse.id
        )
        db_session.add(admin)
        db_session.commit()
        
        assert str(test_order.id) in str(admin)
        assert str(test_user_nurse.id) in str(admin)

class TestCRUDFunctions:
    def test_get_multi_by_doctor(self, db_session, test_user_doctor, test_drug):
        """Test get_multi_by_doctor function loads orders with administrations."""
        # Create multiple orders for the doctor
        order1 = MedicationOrder(
            patient_name="John Doe",
            drug_id=test_drug.id,
            dosage=2,
            schedule="Every 8 hours",
            status=OrderStatus.active,
            doctor_id=test_user_doctor.id,
            created_at=datetime.utcnow()
        )
        order2 = MedicationOrder(
            patient_name="Jane Smith",
            drug_id=test_drug.id,
            dosage=1,
            schedule="Every 12 hours",
            status=OrderStatus.completed,
            doctor_id=test_user_doctor.id,
            created_at=datetime.utcnow()
        )
        db_session.add_all([order1, order2])
        db_session.commit()
        
        # Create administrations for the orders
        admin1 = MedicationAdministration(
            order_id=order1.id,
            nurse_id=1  # Mock nurse ID
        )
        admin2 = MedicationAdministration(
            order_id=order2.id,
            nurse_id=1  # Mock nurse ID
        )
        db_session.add_all([admin1, admin2])
        db_session.commit()
        
        # Test the function
        orders = get_multi_by_doctor(db_session, test_user_doctor.id)
        
        assert len(orders) == 2
        assert orders[0].patient_name == "John Doe"
        assert orders[1].patient_name == "Jane Smith"
        
        # Check that administrations are loaded
        assert len(orders[0].administrations) == 1
        assert len(orders[1].administrations) == 1
        assert orders[0].administrations[0].order_id == order1.id
        assert orders[1].administrations[0].order_id == order2.id
    
    def test_get_multi_by_doctor_no_orders(self, db_session, test_user_doctor):
        """Test get_multi_by_doctor returns empty list when doctor has no orders."""
        orders = get_multi_by_doctor(db_session, test_user_doctor.id)
        assert len(orders) == 0
    
    def test_get_multi_by_doctor_other_doctor_orders(self, db_session, test_user_doctor, test_drug):
        """Test get_multi_by_doctor only returns orders for the specified doctor."""
        # Create another doctor
        other_doctor = User(
            email="other@test.com",
            role=UserRole.doctor,
            api_key="other_key",
            hashed_password="password"
        )
        db_session.add(other_doctor)
        db_session.commit()
        
        # Create orders for both doctors
        order1 = MedicationOrder(
            patient_name="John Doe",
            drug_id=test_drug.id,
            dosage=2,
            schedule="Every 8 hours",
            status=OrderStatus.active,
            doctor_id=test_user_doctor.id,
            created_at=datetime.utcnow()
        )
        order2 = MedicationOrder(
            patient_name="Jane Smith",
            drug_id=test_drug.id,
            dosage=1,
            schedule="Every 12 hours",
            status=OrderStatus.active,
            doctor_id=other_doctor.id,
            created_at=datetime.utcnow()
        )
        db_session.add_all([order1, order2])
        db_session.commit()
        
        # Test that only the first doctor's orders are returned
        orders = get_multi_by_doctor(db_session, test_user_doctor.id)
        assert len(orders) == 1
        assert orders[0].patient_name == "John Doe"
        assert orders[0].doctor_id == test_user_doctor.id 