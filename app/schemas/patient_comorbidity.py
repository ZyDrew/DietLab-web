from pydantic import BaseModel, ConfigDict

class PatientComorbidityCreate(BaseModel):
    patient_id: int
    comorbidity_id: int

class PatientComorbidityResponse(PatientComorbidityCreate):
    id: int

    #Allow Pydantic to read SQLAlchemy's python object as a dictionnary
    model_config = ConfigDict(from_attributes=True)