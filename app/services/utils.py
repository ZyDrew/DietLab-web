from datetime import date
from app.models.patients import Patients

def calculate_age(birth_date: date) -> int:
    today = date.today()
    
    #Edge case - 29 february
    try:
        birthday_this_year = birth_date.replace(year=today.year)
    except ValueError:
        birthday_this_year = birth_date.replace(year=today.year, month=3, day=1)
    
    # IF BIRTHDAY DIDN'T ALREADY OCCUR WE REMOVE 1 YEAR
    if birthday_this_year > today:
        return today.year - birth_date.year - 1
    else:
        return today.year - birth_date.year

def patient_exist(patient_id: int, db):
    patient = db.query(Patients).filter(Patients.id == patient_id).first()

    if patient is None:
        return False
    return True