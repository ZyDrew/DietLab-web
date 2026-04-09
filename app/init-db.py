from app.database import engine, Base
from app.models import patients, patient_measurement, patient_comorbidity, meal_plan, meal_plan_food, foods, recipe_food, recipes, comorbidities, appointments

def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("Tables créées avec succès !")