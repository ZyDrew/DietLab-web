from datetime import date

from app.models.enums import GenderEnum, MealPlanEnum
from app.models.meal_plan import MealPlan
from app.models.meal_plan_food import MealPlanFood
from app.models.patients import Patients
from tests.helpers import make_food

def test_delete_food_from_meal_plan(client, db):
    jane = Patients(lastname="Doe", firstname="Jane", gender=GenderEnum.FEMALE,
                            birthdate=date(1975, 10, 25), notes="Diabétique")

    db.add(jane)
    db.flush()

    food_a = make_food("Test food A")
    food_b = make_food("Test food B")
    db.add_all([food_a, food_b])
    db.flush()

    plan = MealPlan(patient_id=jane.id, number=1, name="Test plan", start_date=date.today())
    db.add(plan)
    db.flush()

    relation_a = MealPlanFood(plan_id=plan.id, food_id=food_a.id, quantity=100,
                        period=MealPlanEnum.BREAKFAST, frequency=7)
    relation_b = MealPlanFood(plan_id=plan.id, food_id=food_b.id, quantity=100,
                        period=MealPlanEnum.DINNER, frequency=7)
    db.add_all([relation_a, relation_b])
    db.flush()

    response = client.delete(f"/api/meal_plans/{plan.id}/foods/{relation_b.id}")

    assert response.status_code == 204
    assert db.query(MealPlanFood).filter_by(plan_id=plan.id, food_id=food_b.id).first() is None
    assert db.query(MealPlanFood).filter_by(plan_id=plan.id, food_id=food_a.id).first() is not None

def test_modify_food_from_meal_plan(client, db):
    jane = Patients(lastname="Doe", firstname="Jane", gender=GenderEnum.FEMALE,
                            birthdate=date(1975, 10, 25), notes="Diabétique")

    db.add(jane)
    db.flush()

    food_a = make_food("Test food A")
    food_b = make_food("Test food B")
    db.add_all([food_a, food_b])
    db.flush()

    plan = MealPlan(patient_id=jane.id, number=1, name="Test plan", start_date=date.today())
    db.add(plan)
    db.flush()

    relation_a = MealPlanFood(plan_id=plan.id, food_id=food_a.id, quantity=100,
                                period=MealPlanEnum.BREAKFAST, frequency=7)
    relation_b = MealPlanFood(plan_id=plan.id, food_id=food_b.id, quantity=100,
                                period=MealPlanEnum.DINNER, frequency=7)
    db.add_all([relation_a, relation_b])
    db.flush()

    response = client.put(f"/api/meal_plans/{plan.id}/foods/{relation_b.id}", json={"food_id": food_b.id, "quantity": 200, "period": MealPlanEnum.DINNER, "frequency": 7})

    assert response.status_code == 200
    assert db.query(MealPlanFood).filter_by(plan_id=plan.id, food_id=food_b.id).first().quantity == 200
    assert db.query(MealPlanFood).filter_by(plan_id=plan.id, food_id=food_a.id).first().quantity == 100