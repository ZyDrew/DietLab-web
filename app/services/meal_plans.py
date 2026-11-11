from collections import defaultdict
from sqlalchemy import case
from sqlalchemy.orm import Session, joinedload
from app.models.meal_plan import MealPlan
from app.models.meal_plan_food import MealPlanFood
from app.services.nutritions import calculate_macro
from app.models.enums import MEAL_PLAN_PERIOD_ORDER

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


# Sort key: position of the period in MEAL_PLAN_PERIOD_ORDER.
_PERIOD_SORT_KEY = case(
    *[(MealPlanFood.period == period, position)
      for position, period in enumerate(MEAL_PLAN_PERIOD_ORDER)],
    else_=len(MEAL_PLAN_PERIOD_ORDER),
)


def get_meal_plan_foods(db: Session, plan_id: int) -> list[MealPlanFood]:
    return (
        db.query(MealPlanFood)
        .filter(MealPlanFood.plan_id == plan_id)
        .options(joinedload(MealPlanFood.food))
        .order_by(_PERIOD_SORT_KEY, MealPlanFood.id)
        .all()
    )
