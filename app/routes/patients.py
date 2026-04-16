from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.patients import PatientResponse, PatientCreate
from app.models.patients import Patients

patients_router = APIRouter(
    prefix="/patients",
    tags=["patients"]
)

# SELECT ALL PATIENTS
@patients_router.get("/", response_model=list[PatientResponse])
def get_patients(db: Session = Depends(get_db)):
    return db.query(Patients).all()

# SELECT PATIENT BASE ON ID
@patients_router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(Patients).filter(Patients.id == patient_id).first()

    if patient is None:
        raise HTTPException(404, "Patient introuvable")
    
    return patient

# INSERT NEW PATIENT
@patients_router.post("/", response_model=PatientResponse)
def create_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    #model_dump converts the PatientCreate object into a Python dictionnary. Allows to decompress into Patient's constructor
    new_patient = Patients(**patient.model_dump())
    db.add(new_patient)
    db.commit()
    #After commit, SQLAlchemy doesn't know the object ID create by the DB.
    #"refresh" forces SQLAlchemy to read the DB's object again and register the ID before returning the new created object
    db.refresh(new_patient)
    return new_patient


# MODIFY ONE PATIENT
@patients_router.put("/{patient_id}", response_model=PatientResponse)
def modify_patient(patient_id: int, patient: PatientCreate, db: Session = Depends(get_db)):
    upd_patient = db.query(Patients).filter(Patients.id == patient_id).first()

    if upd_patient is None:
        raise HTTPException(404, "Patient à modifier, introuvable")
    
    db.query(Patients).filter(Patients.id == patient_id).update(patient.model_dump())
    db.commit()
    db.refresh(upd_patient)

    return upd_patient

# DELETE ONE PATIENT
@patients_router.delete("/{patient_id}", status_code=204)
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(Patients).filter(Patients.id == patient_id).first()

    if patient is None:
        raise HTTPException(404, "Patient à supprimer, introuvable")
    
    db.delete(patient)
    db.commit()

    return Response(status_code=204)
