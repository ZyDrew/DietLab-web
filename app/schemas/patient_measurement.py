from pydantic import BaseModel, ConfigDict
import datetime

class PatientMeasurementCreate(BaseModel):
    height: float
    weight: float
    record_date: datetime.date

class PatientMeasurementResponse(PatientMeasurementCreate):
    id: int
    patient_id: int

    #Allow Pydantic to read SQLAlchemy's python object as a dictionnary
    model_config = ConfigDict(from_attributes=True)