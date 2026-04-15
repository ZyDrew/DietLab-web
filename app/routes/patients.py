from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.patients import PatientResponse, PatientCreate
from app.models.patients import Patients

patients_router = APIRouter(
    prefix="/patients",
    tags=["patients"]
)

@patients_router.get("/", response_model=list[PatientResponse])
def get_patients(db: Session = Depends(get_db)):
    return db.query(Patients).all()

@patients_router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(Patients).filter(Patients.id == patient_id).first()

    if patient is None:
        raise HTTPException(404, "Patient introuvable")
    return patient

@patients_router.post("/", response_model=PatientResponse)
def create_patient(patient : PatientCreate, db: Session = Depends(get_db)):
    try:
        #model_dump converts the PatientCreate object into a Python dictionnary. Allows to decompress into Patient's constructor
        new_patient = Patients(**patient.model_dump())
        db.add(new_patient)
        db.commit()
        #After commit, SQLAlchemy doesn't know the object ID create by the DB.
        #"refresh" forces SQLAlchemy to read the DB's object again and register the ID before returning the new created object
        db.refresh(new_patient)
        return new_patient
    finally:
        db.close()