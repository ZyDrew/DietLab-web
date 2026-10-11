from collections import defaultdict
from sqlalchemy.orm import Session, joinedload
from app.models.meal_plan import MealPlan
from app.models.meal_plan_food import MealPlanFood
from app.services.nutritions import calculate_macro

def get_patient_meal_plans(db: Session, patient_id: int) -> list[dict]:
    plans = (
        db.query(MealPlan)
        .filter(MealPlan.patient_id == patient_id)
        .order_by(MealPlan.number)
        .all()
    )
    if not plans:
        return []

    # One query for the foods of ALL plans, grouped in Python
    plan_foods = (
        db.query(MealPlanFood)
        .filter(MealPlanFood.plan_id.in_([p.id for p in plans]))
        .options(joinedload(MealPlanFood.food))
        .all()
    )
    foods_by_plan = defaultdict(list)
    for food in plan_foods:
        foods_by_plan[food.plan_id].append(food)

    result = []
    for plan in plans:
        _, total = calculate_macro(foods_by_plan[plan.id])
        result.append({"plan": plan, "calories": total["calories"]})
    return result