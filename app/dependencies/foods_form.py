from fastapi import Form
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from app.schemas.foods import FoodCreate

def get_foods_form(
    name: str = Form(...),
    calories: float = Form(...),
    proteins: float = Form(...),
    fat: float = Form(...),
    carbs: float = Form(...),
    calcium: float = Form(...),
    iron: float = Form(...),
    vitamin_c: float = Form(...)
) -> FoodCreate:
    try:
        return FoodCreate(
            name=name,
            calories=calories,
            proteins=proteins,
            fat=fat,
            carbs=carbs,
            calcium=calcium,
            iron=iron,
            vitamin_c=vitamin_c
        )
    except ValidationError as exc:
        # FastAPI does not convert a ValidationError raised inside a dependency into RequestValidationError. 
        # It escalates to the generic handler as a 500, so the global form error renderer never saw it.
        # So I re-raise it here
        raise RequestValidationError(exc.errors()) from exc
