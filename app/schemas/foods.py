from pydantic import BaseModel, ConfigDict

class FoodCreate(BaseModel):
    name: str
    calories: float
    proteins: float
    fat: float
    carbs: float
    calcium: float
    iron: float
    vitamin_c: float

class FoodResponse(FoodCreate):
    id: int

    #Allow Pydantic to read SQLAlchemy's python object as a dictionnary
    model_config = ConfigDict(from_attributes=True)