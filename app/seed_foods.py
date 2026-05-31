"""
Script to seed the foods table from ciqual_foods.csv
Safe to run multiple times - skips existing entries
Run: python -m app.seed_foods
"""
import csv
from pathlib import Path
from app.database import SessionLocal
from app.models.foods import Foods

def seed_foods():
    db = SessionLocal()
    csv_path = Path(__file__).parent / "data" / "ciqual_foods.csv"

    try:
        existing_count = db.query(Foods).count()
        if existing_count > 0:
            print(f"Foods table already has {existing_count} entries — skipping seed.")
            return

        with open(csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter=";")
            foods = []
            for row in reader:
                foods.append(Foods(
                    name=row["name"],
                    calories=float(row["calories"]),
                    proteins=float(row["proteins"]),
                    fat=float(row["fat"]),
                    carbs=float(row["carbs"]),
                    calcium=float(row["calcium"]),
                    iron=float(row["iron"]),
                    vitamin_c=float(row["vitamin_c"])
                ))

            db.bulk_save_objects(foods)
            db.commit()
            print(f"Seeded {len(foods)} foods successfully.")

    except Exception as e:
        db.rollback()
        print(f"Error seeding foods: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_foods()