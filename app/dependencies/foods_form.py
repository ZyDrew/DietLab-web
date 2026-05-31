from fastapi import Form
from app.schemas.meal_plan_food import MealPlanFoodCreate
from app.models.enums import MealPlanEnum

def get_food_form(
    food_id: int = Form(...),
    quantity: int = Form(...),
    frequency: int = Form(...),
    period: MealPlanEnum = Form(...)
) -> MealPlanFoodCreate:
    return MealPlanFoodCreate(
        food_id=food_id,
        quantity=quantity,
        frequency=frequency,
        period=period
    )