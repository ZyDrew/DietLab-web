from app.models.foods import Foods

def make_food(name: str) -> Foods:
    return Foods(name=name, calories=0, proteins=0, fat=0, carbs=0,
                 calcium=0, iron=0, vitamin_c=0)