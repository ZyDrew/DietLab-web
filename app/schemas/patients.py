from pydantic import BaseModel, ConfigDict
import datetime
from typing import Optional
from app.models.enums import GenderEnum

class PatientCreate(BaseModel):
    lastname: str
    firstname: str
    gender: GenderEnum 
    birthdate: datetime.date
    notes: Optional[str] = None

class PatientResponse(PatientCreate):
    id: int

    #Allow Pydantic to read SQLAlchemy's python object as a dictionnary
    model_config = ConfigDict(from_attributes=True)