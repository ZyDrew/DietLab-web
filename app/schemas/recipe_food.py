from pydantic import BaseModel, ConfigDict
from app.models.enums import UnitEnum

class RecipeFoodCreate(BaseModel):
    recipe_id: int
    food_id: int
    quantity: int
    unit: UnitEnum

class RecipeFoodResponse(RecipeFoodCreate):
    id: int

    #"from_attributes" : Allow Pydantic to read SQLAlchemy's python object as a dictionnary
    #"use_enum_values" : Inside model, it uses directly the value (str, int, etc.) instead of AppointmentEnum.MEMBER
    model_config = ConfigDict(use_enum_values=True, from_attributes=True)