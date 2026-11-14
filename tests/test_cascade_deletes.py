from datetime import date, datetime

import pytest
from sqlalchemy.exc import IntegrityError

from app.models.appointments import Appointments
from app.models.comorbidities import Comorbidities
from app.models.enums import AppointmentEnum, MealPlanEnum, UnitEnum
from app.models.meal_plan import MealPlan
from app.models.meal_plan_food import MealPlanFood
from app.models.patient_comorbidity import PatientComorbidity
from app.models.patient_measurement import PatientMeasurement
from app.models.recipe_food import RecipeFood
from app.models.recipes import Recipes
from tests.helpers import make_food, make_patient


def test_delete_patient_deletes_owned_rows(db):
    patient = make_patient(db)

    measurement = PatientMeasurement(patient_id=patient.id, height=170, weight=60)
    appointment = Appointments(
        patient_id=patient.id,
        date_time=datetime(2026, 1, 5, 9, 0),
        type=AppointmentEnum.FIRST,
    )
    comorbidity = Comorbidities(name="Hypertension")
    db.add_all([measurement, appointment, comorbidity])
    db.flush()

    link = PatientComorbidity(patient_id=patient.id, comorbidity_id=comorbidity.id)
    plan = MealPlan(
        patient_id=patient.id,
        number=1,
        name="Plan de test",
        start_date=date.today(),
    )
    db.add_all([link, plan])
    db.flush()

    food = make_food("Riz complet")
    db.add(food)
    db.flush()
    plan_food = MealPlanFood(
        plan_id=plan.id,
        food_id=food.id,
        quantity=100,
        period=MealPlanEnum.LUNCH,
        frequency=7,
    )
    db.add(plan_food)
    db.flush()

    db.delete(patient)
    db.flush()

    assert db.query(PatientMeasurement).filter_by(id=measurement.id).count() == 0
    assert db.query(Appointments).filter_by(id=appointment.id).count() == 0
    assert db.query(PatientComorbidity).filter_by(id=link.id).count() == 0
    assert db.query(MealPlan).filter_by(id=plan.id).count() == 0
    assert db.query(MealPlanFood).filter_by(id=plan_food.id).count() == 0


def test_delete_food_deletes_its_meal_plan_rows(db):
    patient = make_patient(db)
    food = make_food("Lentilles")
    db.add(food)
    db.flush()

    plan = MealPlan(
        patient_id=patient.id,
        number=1,
        name="Plan de test",
        start_date=date.today(),
    )
    db.add(plan)
    db.flush()

    plan_food = MealPlanFood(
        plan_id=plan.id,
        food_id=food.id,
        quantity=150,
        period=MealPlanEnum.DINNER,
        frequency=2,
    )
    db.add(plan_food)
    db.flush()

    db.delete(food)
    db.flush()

    assert db.query(MealPlanFood).filter_by(id=plan_food.id).count() == 0
    assert db.query(MealPlan).filter_by(id=plan.id).count() == 1


def test_delete_recipe_deletes_its_recipe_food(db):
    recipe = Recipes(name="Soupe de légumes")
    food = make_food("Carotte")
    db.add_all([recipe, food])
    db.flush()

    recipe_food = RecipeFood(
        recipe_id=recipe.id,
        food_id=food.id,
        quantity=200,
        unit=UnitEnum.GRAM,
    )
    db.add(recipe_food)
    db.flush()

    db.delete(recipe)
    db.flush()

    assert db.query(RecipeFood).filter_by(id=recipe_food.id).count() == 0


def test_delete_food_used_by_a_recipe_is_refused(db):
    recipe = Recipes(name="Gratin")
    food = make_food("Pomme de terre")
    db.add_all([recipe, food])
    db.flush()

    recipe_food = RecipeFood(
        recipe_id=recipe.id,
        food_id=food.id,
        quantity=300,
        unit=UnitEnum.GRAM,
    )
    db.add(recipe_food)
    db.flush()

    with pytest.raises(IntegrityError):
        with db.begin_nested():
            db.delete(food)

    assert db.query(RecipeFood).filter_by(id=recipe_food.id).count() == 1


def test_api_delete_comorbidity_succeeds_when_linked(auth_client, db):
    patient = make_patient(db)
    comorbidity = Comorbidities(name="Asthme")
    db.add(comorbidity)
    db.flush()

    link = PatientComorbidity(patient_id=patient.id, comorbidity_id=comorbidity.id)
    db.add(link)
    db.flush()
    link_id = link.id

    response = auth_client.delete(f"/api/comorbidities/{comorbidity.id}")

    assert response.status_code == 204
    assert db.query(PatientComorbidity).filter_by(id=link_id).count() == 0


def test_delete_comorbidity_deletes_patient_links(db):
    patient = make_patient(db)
    comorbidity = Comorbidities(name="Diabète de type 2")
    db.add(comorbidity)
    db.flush()

    link = PatientComorbidity(patient_id=patient.id, comorbidity_id=comorbidity.id)
    db.add(link)
    db.flush()

    db.delete(comorbidity)
    db.flush()

    assert db.query(PatientComorbidity).filter_by(id=link.id).count() == 0
