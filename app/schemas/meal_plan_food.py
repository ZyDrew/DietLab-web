from pydantic import BaseModel, ConfigDict
from app.models.enums import MealPlanEnum

class MealPlanFoodCreate(BaseModel):
    plan_id: int
    food_id: int
    quantity: int
    period: MealPlanEnum
    frequency: int

class MealPlanFoodResponse(MealPlanFoodCreate):
    id: int

    #"from_attributes" : Allow Pydantic to read SQLAlchemy's python object as a dictionnary
    #"use_enum_values" : Inside model, it uses directly the value (str, int, etc.) instead of AppointmentEnum.MEMBER
    model_config = ConfigDict(use_enum_values=True, from_attributes=True)