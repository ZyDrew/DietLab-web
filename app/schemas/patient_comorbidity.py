from pydantic import BaseModel, ConfigDict

class PatientComorbidityCreate(BaseModel):
    comorbidity_id: int

class PatientComorbidityResponse(PatientComorbidityCreate):
    id: int
    patient_id: int

    #Allow Pydantic to read SQLAlchemy's python object as a dictionnary
    model_config = ConfigDict(from_attributes=True)