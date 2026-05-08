from fastapi import Form
import datetime
from app.schemas.patient_measurement import PatientMeasurementCreate

def get_measurement_form(
    height: float = Form(...),
    weight: float = Form(...),
    record_date: datetime.date = Form(...),
) -> PatientMeasurementCreate:
    return PatientMeasurementCreate(
        height=height,
        weight=weight,
        record_date=record_date
    )