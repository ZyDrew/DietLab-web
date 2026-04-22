from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.patients import Patients
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
