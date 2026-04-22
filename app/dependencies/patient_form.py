from fastapi import Form
from typing import Optional
import datetime
from app.schemas.patients import PatientCreate
from app.models.enums import GenderEnum

def get_patient_form(
    lastname: str = Form(...),
    firstname: str = Form(...),
    gender: GenderEnum = Form(...),
    birthdate: datetime.date = Form(...),
    notes: Optional[str] = Form(None)
) -> PatientCreate:
    return PatientCreate(
        lastname=lastname,
        firstname=firstname,
        gender=gender,
        birthdate=birthdate,
        notes=notes
    )