from pydantic import BaseModel, ConfigDict

class ComorbidityCreate(BaseModel):
    name: str

class ComorbidityResponse(ComorbidityCreate):
    id: int

    #Allow Pydantic to read SQLAlchemy's python object as a dictionnary
    model_config = ConfigDict(from_attributes=True)