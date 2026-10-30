from pydantic import BaseModel, ConfigDict, Field
import datetime

class LoginCreate(BaseModel):
    email: str = Field(max_length=255)
    password: str = Field(max_length=128)

class LoginResponse(BaseModel):
    id: int
    email: str
    is_active: bool
    created_at: datetime.datetime

    #Allow Pydantic to read SQLAlchemy's python object as a dictionnary
    model_config = ConfigDict(from_attributes=True)