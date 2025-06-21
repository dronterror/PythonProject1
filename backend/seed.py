import os
from sqlalchemy.orm import Session
from database import SessionLocal, Base, engine
from models import User, UserRole, Drug
import secrets

# Create all tables (if not already created)
Base.metadata.create_all(bind=engine)

def seed_users(db: Session):
    if db.query(User).count() == 0:
        users = [
            User(email="doctor@valmed.com", role=UserRole.doctor, api_key=secrets.token_hex(16), hashed_password="doctorpass"),
            User(email="nurse@valmed.com", role=UserRole.nurse, api_key=secrets.token_hex(16), hashed_password="nursepass"),
            User(email="pharmacist@valmed.com", role=UserRole.pharmacist, api_key=secrets.token_hex(16), hashed_password="pharmacistpass"),
        ]
        db.add_all(users)
        db.commit()
        print("Seeded users.")
    else:
        print("Users already seeded.")

def seed_drugs(db: Session):
    if db.query(Drug).count() == 0:
        drugs = [
            Drug(name="Paracetamol", form="tablet", strength="500mg", current_stock=1000, low_stock_threshold=100),
            Drug(name="Ibuprofen", form="tablet", strength="200mg", current_stock=800, low_stock_threshold=80),
            Drug(name="Amoxicillin", form="capsule", strength="250mg", current_stock=500, low_stock_threshold=50),
        ]
        db.add_all(drugs)
        db.commit()
        print("Seeded drugs.")
    else:
        print("Drugs already seeded.")

def main():
    db = SessionLocal()
    try:
        seed_users(db)
        seed_drugs(db)
    finally:
        db.close()

if __name__ == "__main__":
    main() 