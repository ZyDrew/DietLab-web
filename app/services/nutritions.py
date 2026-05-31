def calculate_bej(gender: str, age: int, height: float, weight: float):
    height = height / 100
    match(gender):
        case "male":
            if age >= 0 and age < 3:
                return ((28.2 * weight) + (859 * height) - 371)
            elif age >= 3 and age < 10:
                return ((15.1 * weight) + (74.2 * height) + 306)
            elif age >= 10 and age < 18:
                return ((15.6 * weight) + (266 * height) + 299)
            elif age >= 18 and age < 30:
                return ((14.4 * weight) + (313 * height) + 113)
            elif age >= 30 and age < 60:
                return ((11.4 * weight) + (541 * height) - 137)
            elif age >= 60:
                return ((11.4 * weight) + (541 * height) - 256)  

        case "female":
            if age >= 0 and age < 3:
                return ((30.4 * weight) + (703 * height) - 287)
            elif age >= 3 and age < 10:
                return ((15.9 * weight) + (210 * height) + 349)
            elif age >= 10 and age < 18:
                return ((9.4 * weight) + (249 * height) + 462)
            elif age >= 18 and age < 30:
                return ((10.4 * weight) + (615 * height) - 282)
            elif age >= 30 and age < 60:
                return ((8.18 * weight) + (502 * height) - 11.6)
            elif age >= 60:
                return ((8.52 * weight) + (421 * height) + 10.7) 

        case _:
            raise ValueError(f"Genre inconnu : {gender}")

def calculate_nap(gender: str, age: int, height: float, weight: float, nap: float):
    return calculate_bej(gender, age, height, weight) * nap

def calculate_bmi(height: float, weight: float):
    height = height / 100

    bmi = (weight / (height ** 2))

    if bmi < 18.5:
        category = "underweight"
    elif bmi < 25:
        category = "normal"
    elif bmi < 30:
        category = "overweight"
    else:
        category = "obese"

    return bmi, category
    
def calculate_macro(meal_plan_foods: list):
    result = []
    total = {
        "calories" : 0,
        "proteins" : 0,
        "fat" : 0,
        "carbs" : 0,
        "calcium" : 0,
        "iron" : 0,
        "vitamin_c" : 0
    }

    for item in meal_plan_foods:
        factor = (item.quantity / 100) * (item.frequency / 7)

        food = {
            "food_name": item.food.name,
            "quantity": item.quantity,
            "frequency": item.frequency,
            "period": item.period.value,
            "period_label": item.period.label,
            "calories": round(float(item.food.calories) * factor, 2),
            "proteins": round(float(item.food.proteins) * factor, 2),
            "fat": round(float(item.food.fat) * factor, 2),
            "carbs": round(float(item.food.carbs) * factor, 2),
            "calcium": round(float(item.food.calcium) * factor, 2),
            "iron": round(float(item.food.iron) * factor, 2),
            "vitamin_c": round(float(item.food.vitamin_c) * factor, 2)
        }
        
        result.append(food)

        total["calories"] += food["calories"]
        total["proteins"] += food["proteins"]
        total["fat"] += food["fat"]
        total["carbs"] += food["carbs"]
        total["calcium"] += food["calcium"]
        total["iron"] += food["iron"]
        total["vitamin_c"] += food["vitamin_c"]
    
    total = {k: round(v, 2) for k, v in total.items()}
    
    return result, total
