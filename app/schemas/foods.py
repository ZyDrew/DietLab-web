from typing import Annotated
from pydantic import BaseModel, ConfigDict, Field, StringConstraints

class FoodCreate(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False)

    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=300)]
    calories: float = Field(ge=0, le=99_999_999.99)
    proteins: float = Field(ge=0, le=99_999_999.99)
    fat: float = Field(ge=0, le=99_999_999.99)
    carbs: float = Field(ge=0, le=99_999_999.99)
    calcium: float = Field(ge=0, le=99_999_999.99)
    iron: float = Field(ge=0, le=99_999_999.99)
    vitamin_c: float = Field(ge=0, le=99_999_999.99)


class FoodResponse(FoodCreate):
    id: int
    source: str

    #Allow Pydantic to read SQLAlchemy's python object as a dictionnary
    model_config = ConfigDict(from_attributes=True)