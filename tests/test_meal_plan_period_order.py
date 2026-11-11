from app.models.enums import MealPlanEnum, MEAL_PLAN_PERIOD_ORDER

def test_meal_plan_period_order():
    assert len(MEAL_PLAN_PERIOD_ORDER) == len(set(MEAL_PLAN_PERIOD_ORDER))
    assert set(MEAL_PLAN_PERIOD_ORDER) == set(MealPlanEnum)
    