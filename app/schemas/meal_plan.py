from pydantic import BaseModel, ConfigDict
import datetime

class MealPlanCreate(BaseModel):
    start_date: datetime.date

class MealPlanResponse(MealPlanCreate):
    id: int
    patient_id: int

    #Allow Pydantic to read SQLAlchemy's python object as a dictionnary
    model_config = ConfigDict(from_attributes=True)