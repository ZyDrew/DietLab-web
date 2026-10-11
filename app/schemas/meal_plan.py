from typing import Optional
from pydantic import BaseModel, ConfigDict
import datetime

class MealPlanCreate(BaseModel):
    name: str
    goal: Optional[str] = None

class MealPlanResponse(MealPlanCreate):
    id: int
    patient_id: int
    start_date: datetime.date
    number: int

    #Allow Pydantic to read SQLAlchemy's python object as a dictionnary
    model_config = ConfigDict(from_attributes=True)