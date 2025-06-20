from fastapi import FastAPI, Depends, HTTPException, status, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import models, schemas, crud, auth, blockchain
from database import engine, Base, SessionLocal
from datetime import timedelta
from typing import List
import uvicorn

app = FastAPI()
templates = Jinja2Templates(directory="templates")

Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Auth endpoints
@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, form_data.username)
    if not user or not crud.verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

# User registration (for demo)
@app.post("/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db, user)

# Patients
@app.post("/patients", response_model=schemas.PatientOut)
def create_patient(patient: schemas.PatientCreate, db: Session = Depends(get_db), user: models.User = Depends(auth.require_doctor)):
    return crud.create_patient(db, patient)

@app.get("/patients", response_class=HTMLResponse)
def patients_page(request: Request, db: Session = Depends(get_db)):
    patients = crud.get_patients(db)
    return templates.TemplateResponse("patients.html", {"request": request, "patients": patients})

@app.post("/patients", response_class=HTMLResponse)
def add_patient(request: Request, name: str = Form(...), date_of_birth: str = Form(...), gender: str = Form(...), contact_info: str = Form(None), diagnosis: str = Form(None), db: Session = Depends(get_db)):
    from datetime import datetime
    patient = schemas.PatientCreate(
        name=name,
        date_of_birth=datetime.strptime(date_of_birth, "%Y-%m-%d").date(),
        gender=gender,
        contact_info=contact_info,
        diagnosis=diagnosis
    )
    crud.create_patient(db, patient)
    patients = crud.get_patients(db)
    return templates.TemplateResponse("patients.html", {"request": request, "patients": patients})

# Drugs
@app.post("/drugs", response_model=schemas.DrugOut)
def create_drug(drug: schemas.DrugCreate, db: Session = Depends(get_db), user: models.User = Depends(auth.require_analyst)):
    return crud.create_drug(db, drug)

@app.get("/drugs", response_class=HTMLResponse)
def drugs_page(request: Request, db: Session = Depends(get_db)):
    drugs = crud.get_drugs(db)
    return templates.TemplateResponse("drugs.html", {"request": request, "drugs": drugs})

@app.post("/drugs", response_class=HTMLResponse)
def add_drug(request: Request, name: str = Form(...), manufacturer: str = Form(None), price_per_unit: float = Form(...), effectiveness_score: float = Form(None), db: Session = Depends(get_db)):
    drug = schemas.DrugCreate(
        name=name,
        manufacturer=manufacturer,
        price_per_unit=price_per_unit,
        effectiveness_score=effectiveness_score
    )
    crud.create_drug(db, drug)
    drugs = crud.get_drugs(db)
    return templates.TemplateResponse("drugs.html", {"request": request, "drugs": drugs})

# Prescriptions
@app.post("/prescriptions", response_model=schemas.PrescriptionOut)
def create_prescription(prescription: schemas.PrescriptionCreate, db: Session = Depends(get_db), user: models.User = Depends(auth.require_doctor)):
    return crud.create_prescription(db, prescription)

@app.get("/prescriptions", response_class=HTMLResponse)
def prescriptions_page(request: Request, db: Session = Depends(get_db)):
    prescriptions = crud.get_prescriptions(db)
    return templates.TemplateResponse("prescriptions.html", {"request": request, "prescriptions": prescriptions})

@app.post("/prescriptions", response_class=HTMLResponse)
def add_prescription(request: Request, patient_id: int = Form(...), drug_id: int = Form(...), prescription_date: str = Form(None), dosage: str = Form(None), duration: str = Form(None), cost_at_time_of_prescription: float = Form(None), effectiveness_at_time_of_prescription: float = Form(None), db: Session = Depends(get_db)):
    from datetime import datetime
    presc_date = None
    if prescription_date:
        try:
            presc_date = datetime.strptime(prescription_date, "%Y-%m-%dT%H:%M")
        except Exception:
            presc_date = None
    prescription = schemas.PrescriptionCreate(
        patient_id=patient_id,
        drug_id=drug_id,
        prescription_date=presc_date,
        dosage=dosage,
        duration=duration,
        cost_at_time_of_prescription=cost_at_time_of_prescription,
        effectiveness_at_time_of_prescription=effectiveness_at_time_of_prescription,
        calculated_icer=None,
        qaly_score=None
    )
    crud.create_prescription(db, prescription)
    prescriptions = crud.get_prescriptions(db)
    return templates.TemplateResponse("prescriptions.html", {"request": request, "prescriptions": prescriptions})

# ICER calculation endpoint (for dashboard)
@app.get("/metrics/icer")
def get_icer(db: Session = Depends(get_db), user: models.User = Depends(auth.require_analyst)):
    prescriptions = crud.get_prescriptions(db)
    if not prescriptions:
        return {"icer": None}
    # Simple ICER calculation: average of all
    costs = [p.cost_at_time_of_prescription for p in prescriptions if p.cost_at_time_of_prescription and p.effectiveness_at_time_of_prescription]
    effects = [p.effectiveness_at_time_of_prescription for p in prescriptions if p.cost_at_time_of_prescription and p.effectiveness_at_time_of_prescription]
    if not costs or not effects or sum(effects) == 0:
        return {"icer": None}
    delta_cost = sum(costs)
    delta_effect = sum(effects)
    icer = delta_cost / delta_effect if delta_effect else None
    return {"icer": icer}

# Blockchain PoC endpoints
@app.post("/blockchain/add-record-hash")
def add_record_hash(patient_id: int, data_hash: str, user: models.User = Depends(auth.get_current_active_user)):
    return blockchain.add_record_hash(patient_id, data_hash)

@app.get("/blockchain/verify-record-hash")
def verify_record_hash(patient_id: int, index: int, user: models.User = Depends(auth.get_current_active_user)):
    return blockchain.verify_record_hash(patient_id, index)

@app.post("/blockchain/grant-access")
def grant_access(patient_id: int, recipient_address: str, user: models.User = Depends(auth.get_current_active_user)):
    return blockchain.grant_access(patient_id, recipient_address)

@app.post("/blockchain/revoke-access")
def revoke_access(patient_id: int, recipient_address: str, user: models.User = Depends(auth.get_current_active_user)):
    return blockchain.revoke_access(patient_id, recipient_address)

# Basic HTML UI
@app.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    # Get ICER
    prescriptions = crud.get_prescriptions(db)
    costs = [p.cost_at_time_of_prescription for p in prescriptions if p.cost_at_time_of_prescription and p.effectiveness_at_time_of_prescription]
    effects = [p.effectiveness_at_time_of_prescription for p in prescriptions if p.cost_at_time_of_prescription and p.effectiveness_at_time_of_prescription]
    icer = sum(costs) / sum(effects) if costs and effects and sum(effects) != 0 else None
    # Get QALY
    qaly_scores = [p.qaly_score for p in prescriptions if p.qaly_score is not None]
    qaly = sum(qaly_scores) / len(qaly_scores) if qaly_scores else None
    # Top-3 costly drugs
    drugs = crud.get_drugs(db)
    top_drugs = sorted(drugs, key=lambda d: d.price_per_unit if d.price_per_unit else 0, reverse=True)[:3]
    return templates.TemplateResponse("dashboard.html", {"request": request, "icer": icer, "qaly": qaly, "top_drugs": top_drugs})

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Add more HTML endpoints as needed for patients, drugs, prescriptions

@app.get("/metrics/qaly")
def get_qaly(db: Session = Depends(get_db), user: models.User = Depends(auth.require_analyst)):
    prescriptions = crud.get_prescriptions(db)
    qaly_scores = [p.qaly_score for p in prescriptions if p.qaly_score is not None]
    if not qaly_scores:
        return {"qaly": None}
    avg_qaly = sum(qaly_scores) / len(qaly_scores)
    return {"qaly": avg_qaly}

# Analysis endpoints
@app.post("/analyses", response_model=schemas.AnalysisOut)
def create_analysis(analysis: schemas.AnalysisCreate, db: Session = Depends(get_db)):
    return crud.create_analysis(db, analysis)

@app.get("/analyses", response_model=List[schemas.AnalysisOut])
def get_analyses(db: Session = Depends(get_db)):
    return crud.get_analyses(db)

@app.get("/analyses/{analysis_id}", response_model=schemas.AnalysisOut)
def get_analysis(analysis_id: int, db: Session = Depends(get_db)):
    return crud.get_analysis(db, analysis_id)

# Report endpoints
@app.post("/reports", response_model=schemas.ReportOut)
def create_report(report: schemas.ReportCreate, db: Session = Depends(get_db)):
    return crud.create_report(db, report)

@app.get("/reports", response_model=List[schemas.ReportOut])
def get_reports(db: Session = Depends(get_db)):
    return crud.get_reports(db)

@app.get("/reports/{report_id}", response_model=schemas.ReportOut)
def get_report(report_id: int, db: Session = Depends(get_db)):
    return crud.get_report(db, report_id)

# AuditLog endpoints
@app.post("/audit-logs", response_model=schemas.AuditLogOut)
def create_audit_log(audit_log: schemas.AuditLogCreate, db: Session = Depends(get_db)):
    return crud.create_audit_log(db, audit_log)

@app.get("/audit-logs", response_model=List[schemas.AuditLogOut])
def get_audit_logs(db: Session = Depends(get_db)):
    return crud.get_audit_logs(db)

@app.get("/audit-logs/{log_id}", response_model=schemas.AuditLogOut)
def get_audit_log(log_id: int, db: Session = Depends(get_db)):
    return crud.get_audit_log(db, log_id)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 