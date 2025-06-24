import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend import models, database
from sqlalchemy.orm import Session
import uuid

client = TestClient(app)

def create_user(role, username, password="testpass"):
    # This function assumes you have a user creation endpoint or a way to seed users for tests
    # Replace with actual user creation logic or use factories if available
    response = client.post("/users/", json={"username": username, "password": password, "role": role})
    assert response.status_code == 201
    return response.json()

def login(username, password="testpass"):
    response = client.post("/token", data={"username": username, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]

@pytest.mark.e2e
@pytest.mark.usefixtures("db_session")
def test_full_medication_lifecycle(db_session: Session):
    # Arrange: Create users
    pharmacist = create_user("pharmacist", "pharm1")
    doctor = create_user("doctor", "doc1")
    nurse = create_user("nurse", "nurse1")

    pharmacist_token = login("pharm1")
    doctor_token = login("doc1")
    nurse_token = login("nurse1")

    # Pharmacist creates a drug
    drug_resp = client.post(
        "/drugs/",
        json={"name": "TestDrug", "current_stock": 10},
        headers={"Authorization": f"Bearer {pharmacist_token}"}
    )
    assert drug_resp.status_code == 201
    drug = drug_resp.json()
    drug_id = drug["id"]

    # Doctor prescribes the drug to a patient in a ward
    order_resp = client.post(
        "/orders/",
        json={"drug_id": drug_id, "patient_id": str(uuid.uuid4()), "ward_id": str(uuid.uuid4())},
        headers={"Authorization": f"Bearer {doctor_token}"}
    )
    assert order_resp.status_code == 201
    order = order_resp.json()
    order_id = order["id"]
    ward_id = order["ward_id"]

    # Nurse administers the order
    admin_resp = client.post(
        "/administrations/",
        json={"order_id": order_id},
        headers={"Authorization": f"Bearer {nurse_token}"}
    )
    assert admin_resp.status_code == 201

    # Pharmacist checks drug stock
    stock_resp = client.get(
        f"/drugs/stock/{drug_id}/{ward_id}",
        headers={"Authorization": f"Bearer {pharmacist_token}"}
    )
    assert stock_resp.status_code == 200
    stock = stock_resp.json()
    assert stock["current_stock"] == 9 