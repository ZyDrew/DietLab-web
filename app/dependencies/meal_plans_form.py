from fastapi import Form
from app.schemas.meal_plan import MealPlanCreate

def get_meal_plans_form(
    name: str = Form(...),
    goal: str = Form(None),
) -> MealPlanCreate:
    return MealPlanCreate(
        name=name,
        goal=goal
    )