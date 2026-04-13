from pydantic import BaseModel, ConfigDict
import datetime
from typing import Optional

class PatientCreate(BaseModel):
    lastname: str
    firstname: str
    birthdate: datetime.date
    notes: Optional[str]

class PatientResponse(PatientCreate):
    id: int

    #Allow Pydantic to read SQLAlchemy's python object as a dictionnary
    model_config = ConfigDict(from_attributes=True)