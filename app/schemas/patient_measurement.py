from pydantic import BaseModel, ConfigDict
import datetime

class PatientMeasurementCreate(BaseModel):
    patient_id: int
    height: float
    weight: float
    record_date: datetime.date

class PatientMesurementResponse(PatientMeasurementCreate):
    id: int

    #"from_attributes" : Allow Pydantic to read SQLAlchemy's python object as a dictionnary
    #"use_enum_values" : Inside model, it uses directly the value (str, int, etc.) instead of AppointmentEnum.MEMBER
    model_config = ConfigDict(use_enum_values=True, from_attributes=True)