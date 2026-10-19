"""
Seed fictional demonstration data (patients, measurements, comorbidities, meal plans).
Safe to run multiple times: does nothing if patients already exist.
Requires the foods table to be seeded first: python -m app.seed_foods
Run: python -m app.seed_demo
"""
from datetime import date, timedelta
from app.database import SessionLocal
from app.models.comorbidities import Comorbidities
from app.models.enums import GenderEnum, MealPlanEnum
from app.models.foods import Foods
from app.models.meal_plan import MealPlan
from app.models.meal_plan_food import MealPlanFood
from app.models.patient_comorbidity import PatientComorbidity
from app.models.patient_measurement import PatientMeasurement
from app.models.patients import Patients


def get_food(db, name: str) -> Foods:
    food = db.query(Foods).filter(Foods.name == name).first()
    if food is None:
        raise ValueError(f"Food not found: {name!r} (was app.seed_foods run first?)")
    return food


def add_plan(db, patient_id, number, name, goal, start_date, items):
    """Create a meal plan and its foods. items: (food name, quantity, period, frequency)."""
    plan = MealPlan(patient_id=patient_id, number=number, name=name, goal=goal, start_date=start_date)
    db.add(plan)
    db.flush()  # assigns plan.id without committing
    for food_name, quantity, period, frequency in items:
        db.add(MealPlanFood(
            plan_id=plan.id,
            food_id=get_food(db, food_name).id,
            quantity=quantity,
            period=period,
            frequency=frequency,
        ))


def seed_demo():
    db = SessionLocal()
    try:
        if db.query(Patients).count() > 0:
            print("Demo data: patients already exist, skipping.")
            return

        today = date.today()

        diabetes = Comorbidities(name="Diabète")
        hypertension = Comorbidities(name="Hypertension")
        jane = Patients(lastname="Doe", firstname="Jane", gender=GenderEnum.FEMALE,
                        birthdate=date(1975, 10, 25), notes="Diabétique")
        john = Patients(lastname="Doe", firstname="John", gender=GenderEnum.MALE,
                        birthdate=date(1965, 6, 12), notes=None)
        db.add_all([diabetes, hypertension, jane, john])
        db.flush()

        db.add_all([
            PatientComorbidity(patient_id=jane.id, comorbidity_id=diabetes.id),
            PatientComorbidity(patient_id=john.id, comorbidity_id=hypertension.id),
        ])

        db.add_all([
            PatientMeasurement(patient_id=jane.id, height=168, weight=73, record_date=today - timedelta(days=90)),
            PatientMeasurement(patient_id=jane.id, height=168, weight=71, record_date=today - timedelta(days=60)),
            PatientMeasurement(patient_id=jane.id, height=168, weight=69.5, record_date=today - timedelta(days=30)),
            PatientMeasurement(patient_id=john.id, height=180, weight=92, record_date=today - timedelta(days=60)),
            PatientMeasurement(patient_id=john.id, height=180, weight=90, record_date=today - timedelta(days=30)),
        ])

        add_plan(db, jane.id, 1, "Premier suivi - 1 mois",
                "Plan adapté pour une perte douce avec diabète",
                today - timedelta(days=90), [
                    ("Oeuf dur", 100, MealPlanEnum.BREAKFAST, 5),
                    ("Chocolat noir 70 % de cacao environ, de dégustation, tablette", 30, MealPlanEnum.EVENING_SNACK, 7),
                    ("Boeuf, entrecôte, partie maigre grillée/poêlée", 250, MealPlanEnum.DINNER, 1),
                ])
        add_plan(db, jane.id, 2, "Suivi longue durée - 6 mois",
                "Plan adapté pour maintient du poids avec diabète",
                today - timedelta(days=30), [
                    ("Fromage frais type petit suisse, aux fruits, 2-3% MG, sucré", 150, MealPlanEnum.BREAKFAST, 4),
                    ("Poulet, viande crue", 250, MealPlanEnum.DINNER, 5),
                ])
        add_plan(db, john.id, 1, "Suivi longue durée - 3 mois",
                "Plan adapté pour une transition alimentaire suite à une chimio",
                today - timedelta(days=60), [
                    ("Fromage blanc, nature, 0% MG, enrichi en vitamine D", 150, MealPlanEnum.BREAKFAST, 6),
                    ("Petits pois, cuits", 125, MealPlanEnum.LUNCH, 5),
                    ("Riz complet, cuit, sans sel ajouté", 200, MealPlanEnum.DINNER, 2),
                ])

        db.commit()  # single commit: all or nothing
        print("Demo data created.")

    except Exception as e:
        db.rollback()
        print(f"Error seeding fake data: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_demo()