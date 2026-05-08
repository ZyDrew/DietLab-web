from typing import List

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.dependencies.measurement_form import get_measurement_form
from app.models.comorbidities import Comorbidities
from app.models.meal_plan import MealPlan
from app.models.patient_comorbidity import PatientComorbidity
from app.models.patients import Patients
from app.models.patient_measurement import PatientMeasurement
from app.schemas.patient_measurement import PatientMeasurementCreate
from app.schemas.patients import PatientCreate
from app.dependencies.patient_form import get_patient_form
from pathlib import Path
from datetime import date

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

############################
########  PATIENTS  ########
############################

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

############################
#####  COMORBIDITIES   #####
############################

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


############################
######  MEASUREMENTS  ######
############################

@views_router.delete("/patients/{patient_id}/measurements/{measure_id}")
async def delete_measurement(patient_id: int, measure_id: int, request: Request, db: Session = Depends(get_db)):
    patient = patient_exist(patient_id, db)
    if not patient:
        return HTTPException(404, "le patient n'existe pas")

    measure = (
        db.query(PatientMeasurement)
        .filter(PatientMeasurement.patient_id == patient_id)
        .filter(PatientMeasurement.id == measure_id)
        .first()
    )

    if not measure:
        return HTTPException(404, "La mesure n'existe pas")
    
    db.delete(measure)
    db.commit()

    measurements = db.query(PatientMeasurement).filter(PatientMeasurement.patient_id == patient_id).all()

    return templates.TemplateResponse(
        request=request,
        name="patients/measurements_tab.html",
        context={"patient" : patient, "measurements" : measurements}
    )

@views_router.get("/patients/{patient_id}/measurements/new")
def new_measurement_form(patient_id: int, request: Request):
    return templates.TemplateResponse(
        request=request,
        name="patients/measurements_form.html",
        context={"patient_id" : patient_id, "measure" : None, "today" : date.today()}
    )

@views_router.get("/patients/{patient_id}/measurements/{measure_id}/edit")
def edit_measurement_form(patient_id: int, measure_id: int, request: Request, db: Session = Depends(get_db)):
    measure = db.query(PatientMeasurement).filter(PatientMeasurement.id == measure_id).first()

    if not measure:
        return HTTPException(404, "la mesure n'existe pas pour le patient sélectionné")

    return templates.TemplateResponse(
        request=request,
        name="patients/measurements_form.html",
        context={"patient_id" : patient_id, "measure" : measure}
    )

@views_router.post("/patients/{patient_id}/measurements/new")
async def create_measurement(patient_id: int, request: Request, measure: PatientMeasurementCreate = Depends(get_measurement_form), db: Session = Depends(get_db)):
    patient = patient_exist(patient_id, db)
    if not patient:
        return HTTPException(404, "le patient n'existe pas")

    new_measure = PatientMeasurement(patient_id=patient_id, **measure.model_dump())
    db.add(new_measure)
    db.commit()
    
    measurements = db.query(PatientMeasurement).filter(PatientMeasurement.patient_id == patient_id).all()

    return templates.TemplateResponse(
        request=request,
        name="patients/measurements_tab.html",
        context={"patient" : patient, "measurements" : measurements}
    )

@views_router.put("/patients/{patient_id}/measurements/{measure_id}/edit")
async def update_measurement(patient_id: int, measure_id: int, request: Request, measure: PatientMeasurementCreate = Depends(get_measurement_form), db: Session = Depends(get_db)):
    patient = patient_exist(patient_id, db)
    if not patient:
        return HTTPException(404, "Le patient n'existe pas")

    db.query(PatientMeasurement).filter(PatientMeasurement.id == measure_id).update(measure.model_dump())
    db.commit()

    measurements = db.query(PatientMeasurement).filter(PatientMeasurement.patient_id == patient_id).all()

    return templates.TemplateResponse(
        request=request,
        name="patients/measurements_tab.html",
        context={"patient": patient, "measurements": measurements}
    )