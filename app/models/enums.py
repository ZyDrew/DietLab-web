import enum

class UnitEnum(enum.Enum):
    GRAM = "gram"             #gramme - g
    MGRAM = "milligram"       #milligramme - mg
    ML = "ml"                 #millilitre
    CL = "cl"                 #centilitre
    TSP = "tsp"               #teaspoon - cuillère à café
    TBSP = "tbsp"             #tablespoon - cuillère à soupe
    UNIT = "unit"             #pièce - ex: 3 oeufs

class AppointmentEnum(enum.Enum):
    FIRST = "first"           #Premier rendez-vous
    FOLLOW_UP = "follow_up"   #Suivi
    CLOSURE = "closure"       #Dernier rendez-vous

class MealPlanEnum(enum.Enum):
    BREAKFAST = "breakfast"             #Petit déjeuner
    MORNING_SNACK = "morning_snack"     #Collation du matin (10am-10h)
    LUNCH = "lunch"                     #Dîner
    AFTERNOON_SNACK = "afternoon_snack" #Collation de l'après-midi / goûter (4pm-16h)
    DINNER = "dinner"                   #Souper / supper
    EVENING_SNACK = "evening_snack"     #Collation du soir (10pm~ - 22h)
