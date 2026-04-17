from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.patients import PatientResponse, PatientCreate
from app.models.patients import Patients
from app.schemas.patient_comorbidity import PatientComorbidityCreate, PatientComorbidityResponse
from app.models.patient_comorbidity import PatientComorbidity
from app.schemas.patient_measurement import PatientMeasurementCreate, PatientMeasurementResponse
from app.models.patient_measurement import PatientMeasurement

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

# ADD ONE COMORBIDITY TO ONE PATIENT
@patients_router.post("/{patient_id}/comorbidities", response_model=PatientComorbidityResponse)
def add_comorbidity_to_patient(patient_id: int, comorbidity_in: PatientComorbidityCreate, db: Session = Depends(get_db)):
    patient = db.query(Patients).filter(Patients.id == patient_id).first()

    if patient is None:
        raise HTTPException(404, "Patient introuvable")
    
    new_relation = PatientComorbidity(
        patient_id = patient_id,
        comorbidity_id = comorbidity_in.comorbidity_id
    )
    db.add(new_relation)
    db.commit()
    db.refresh(new_relation)
    return new_relation

# DELETE ONE RELATION : PATIENT-COMORBIDITY
@patients_router.delete("/{patient_id}/{comorbidity_id}", status_code=204)
def delete_patient(patient_id: int, comorbidity_id: int, db: Session = Depends(get_db)):
    relation = db.query(PatientComorbidity).filter(PatientComorbidity.patient_id == patient_id and PatientComorbidity.comorbidity_id == comorbidity_id).first()

    if relation is None:
        raise HTTPException(404, "Relation Patient-Comorbidité à supprimer, introuvable")
    
    db.delete(relation)
    db.commit()

    return Response(status_code=204)

# SELECT ALL MEASURES FOR ONE PATIENT
@patients_router.get("/{patient_id}/measurement", response_model=list[PatientMeasurementResponse])
def get_all_measurement(patient_id: int, db: Session = Depends(get_db)):
    return db.query(PatientMeasurement).filter(PatientMeasurement.id == patient_id).all()

# ADD ONE MEASUREMENT TO PATIENT
@patients_router.post("/{patient_id}/measurement", response_model=PatientMeasurementResponse)
def add_measurement_to_patient(patient_id: int, measurement_in: PatientMeasurementCreate, db: Session = Depends(get_db)):
    patient = db.query(Patients).filter(Patients.id == patient_id).first()

    if patient is None:
        raise HTTPException(404, "Patient introuvable")
    
    new_relation = PatientMeasurement(
        patient_id = patient_id,
        **measurement_in.model_dump()
    )

    db.add(new_relation)
    db.commit()
    db.refresh(new_relation)
    return new_relation