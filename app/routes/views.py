from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.comorbidities import Comorbidities
from app.models.meal_plan import MealPlan
from app.models.patient_comorbidity import PatientComorbidity
from app.models.patients import Patients
from app.models.patient_measurement import PatientMeasurement
from app.schemas.patients import PatientCreate
from app.dependencies.patient_form import get_patient_form
from pathlib import Path

views_router = APIRouter()
templates = Jinja2Templates(directory=Path("app") / "templates")

#Why Request class ? as it is not use in the API_Router
#Because Jinja2 needs it to generate correct URL and to be aware on which server it is running

@views_router.get("/")
def dashboard(request: Request, db: Session = Depends(get_db)):
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
    measurements = db.query(PatientMeasurement).filter(PatientMeasurement.patient_id == patient_id).all()
    comorbidities = db.query(PatientComorbidity).filter(PatientComorbidity.patient_id == patient_id).all()
    meal_plans = db.query(MealPlan).filter(MealPlan.patient_id == patient_id).all()

    comorbidities_name = []
    if comorbidities:
        for comorbidity in comorbidities:
            comorbidities_name.append(db.query(Comorbidities).filter(Comorbidities.id == comorbidity.comorbidity_id).first())

    return templates.TemplateResponse(
        request=request,
        name="patients/details.html",
        context={"patient" : patient, "comorbidities" : comorbidities_name, "measurements" : measurements, "meal_plans" : meal_plans}
    )