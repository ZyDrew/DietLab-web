from pydantic import BaseModel, ConfigDict

class RecipeCreate(BaseModel):
    name: str

class RecipeResponse(RecipeCreate):
    id: int

    #Allow Pydantic to read SQLAlchemy's python object as a dictionnary
    model_config = ConfigDict(from_attributes=True)