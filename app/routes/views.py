from typing import List

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models.comorbidities import Comorbidities
from app.models.meal_plan import MealPlan
from app.models.patient_comorbidity import PatientComorbidity
from app.models.patients import Patients
from app.models.patient_measurement import PatientMeasurement
from app.schemas.patients import PatientCreate
from app.dependencies.patient_form import get_patient_form
from pathlib import Path

from app.services.utils import patient_exist

views_router = APIRouter()
templates = Jinja2Templates(directory=Path("app") / "templates")

#Why Request class ? as it is not use in the API_Router
#Because Jinja2 needs it to generate correct URL and to be aware on which server it is running

@views_router.get("/")
def dashboard(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html"
    )

@views_router.get("/patients")
def get_all_patients(request: Request, db: Session = Depends(get_db)):
    patients = db.query(Patients).all()
    return templates.TemplateResponse(
        request=request,
        name="patients/list.html",
        context={"patients" : patients}
    )

@views_router.get("/patients/new")
def new_patient_form(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="patients/form.html"
    )

@views_router.post("/patients/new")
async def create_patient(request: Request, patient: PatientCreate = Depends(get_patient_form), db: Session = Depends(get_db)):
    new_patient = Patients(**patient.model_dump())
    db.add(new_patient)
    db.commit()
    patients = db.query(Patients).all()

    return templates.TemplateResponse(
        request=request,
        name="patients/list.html",
        context={"patients" : patients}
    )

@views_router.get("/patients/{patient_id}")
def get_patient_details(patient_id: int, request: Request, db: Session = Depends(get_db)):
    patient = db.query(Patients).filter(Patients.id == patient_id).first()
    
    if patient is None:
        return HTTPException(404, "Le patient n'existe pas")

    measurements = db.query(PatientMeasurement).filter(PatientMeasurement.patient_id == patient_id).all()
    comorbidities = (
        db.query(PatientComorbidity)
        .filter(PatientComorbidity.patient_id == patient_id)
        .options(joinedload(PatientComorbidity.comorbidity))
        .all()
    )
    meal_plans = db.query(MealPlan).filter(MealPlan.patient_id == patient_id).all()


    return templates.TemplateResponse(
        request=request,
        name="patients/details.html",
        context={"patient" : patient, "comorbidities" : comorbidities, "measurements" : measurements, "meal_plans" : meal_plans}
    )

@views_router.get("/patients/{patient_id}/comorbidities/edit")
def manage_comorbidities(patient_id: int, request: Request, db: Session = Depends(get_db)):
    patient = db.query(Patients).filter(Patients.id == patient_id).first()
    
    if patient is None:
        return HTTPException(404, "Le patient n'existe pas")

    all_comorbidities = db.query(Comorbidities).all()

    patient_comorbidities = (
        db.query(PatientComorbidity)
        .filter(PatientComorbidity.patient_id == patient_id)
        .options(joinedload(PatientComorbidity.comorbidity))
        .all()
    )

    patient_comorbidities_ids = {c.comorbidity_id for c in patient_comorbidities}


    return templates.TemplateResponse(
        request=request,
        name="patients/comorbidities_form.html",
        context={"patient" : patient, "all_comorbidities" : all_comorbidities, "patient_comorbidities_ids" : patient_comorbidities_ids}
    )

@views_router.post("/patients/{patient_id}/comorbidities/edit")
async def manage_comorbidities(patient_id: int, request: Request, db: Session = Depends(get_db), comorbidities_ids: List[int] = Form(default=[])):
    if not patient_exist(patient_id, db):
        return HTTPException(404, "Le patient n'existe pas")

    to_delete = (
        db.query(PatientComorbidity)
        .filter(PatientComorbidity.patient_id == patient_id)
        .all()
    )

    for item in to_delete:
        db.delete(item)
    db.commit()

    for comorbidity in comorbidities_ids:
        new_relation = PatientComorbidity(
            patient_id = patient_id,
            comorbidity_id = comorbidity
        )
        db.add(new_relation)
    
    db.commit()

    comorbidities = (
        db.query(PatientComorbidity)
        .filter(PatientComorbidity.patient_id == patient_id)
        .options(joinedload(PatientComorbidity.comorbidity))
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="patients/comorbidities_list.html",
        context={"comorbidities" : comorbidities}
    )