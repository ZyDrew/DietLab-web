from typing import List

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import case, func
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.dependencies.foods_form import get_food_form
from app.dependencies.measurement_form import get_measurement_form
from app.models.comorbidities import Comorbidities
from app.models.foods import Foods
from app.models.meal_plan import MealPlan
from app.models.meal_plan_food import MealPlanFood
from app.models.patient_comorbidity import PatientComorbidity
from app.models.patients import Patients
from app.models.patient_measurement import PatientMeasurement
from app.schemas.meal_plan import MealPlanCreate
from app.dependencies.meal_plans_form import get_meal_plans_form
from app.schemas.meal_plan_food import MealPlanFoodCreate
from app.schemas.patient_measurement import PatientMeasurementCreate
from app.schemas.patients import PatientCreate
from app.dependencies.patient_form import get_patient_form
from pathlib import Path
from datetime import date

from app.services.nutritions import calculate_macro
from app.services.utils import patient_exist
from app.services.meal_plans import get_patient_meal_plans

views_router = APIRouter()
templates = Jinja2Templates(directory=Path("app") / "templates")

#Why Request class ? as it is not use in the API_Router
#Because Jinja2 needs it to generate correct URL and to be aware on which server it is running

#Get Home - Main page - dashboard
@views_router.get("/")
def dashboard(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html"
    )

############################
########  PATIENTS  ########
############################

# GET PATIENTS LIST INSIDE HOME PAGE
@views_router.get("/patients")
def get_all_patients(request: Request, db: Session = Depends(get_db)):
    patients = db.query(Patients).all()
    return templates.TemplateResponse(
        request=request,
        name="patients/list.html",
        context={"patients" : patients}
    )

# GET PATIENT'S FORM TO CREATE A NEW ONE
@views_router.get("/patients/new")
def new_patient_form(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="patients/form.html",
        context={"edit" : None}
    )

# POST NEW PATIENT WITH FORM'S INFORMATIONS
@views_router.post("/patients/new")
async def create_patient(request: Request, patient: PatientCreate = Depends(get_patient_form), db: Session = Depends(get_db)):
    new_patient = Patients(**patient.model_dump())
    db.add(new_patient)
    db.commit()
    patients = db.query(Patients).all()

    return templates.TemplateResponse(
        request=request,
        name="patients/list.html",
        context={"patients" : patients}
    )

# GET PATIENT'S DETAILS AND ROOT TO DETAILS PAGE
@views_router.get("/patients/{patient_id}")
def get_patient_details(patient_id: int, request: Request, db: Session = Depends(get_db)):
    patient = db.query(Patients).filter(Patients.id == patient_id).first()
    
    if patient is None:
        return HTTPException(404, "Le patient n'existe pas")

    measurements = db.query(PatientMeasurement).filter(PatientMeasurement.patient_id == patient_id).all()
    comorbidities = (
        db.query(PatientComorbidity)
        .filter(PatientComorbidity.patient_id == patient_id)
        .options(joinedload(PatientComorbidity.comorbidity))
        .all()
    )

    meal_plans = get_patient_meal_plans(db, patient_id)

    return templates.TemplateResponse(
        request=request,
        name="patients/details.html",
        context={"patient" : patient, "comorbidities" : comorbidities, "measurements" : measurements, "meal_plans" : meal_plans}
    )

# GET PATIENT'S FORM TO EDIT AN EXISTING ONE
@views_router.get("/patients/{patient_id}/edit")
def edit_patient_form(patient_id: int, request: Request, db: Session = Depends(get_db)):
    patient = patient_exist(patient_id, db)
    if not patient:
        return HTTPException(404, "Le patient n'existe pas")
    
    return templates.TemplateResponse(
        request=request,
        name="patients/form.html",
        context={"patient" : patient, "edit" : True}
    )

# PUT PATIENT'S INFOS AFTER COMPLETING EDITION FORM
@views_router.put("/patients/{patient_id}/edit")
async def update_patient(patient_id: int, request: Request, edit_patient: PatientCreate = Depends(get_patient_form), db: Session = Depends(get_db)):
    if not patient_exist(patient_id, db):
        return HTTPException(404, "Le patient n'existe pas")
    
    db.query(Patients).filter(Patients.id == patient_id).update(edit_patient.model_dump())
    db.commit()

    patients = db.query(Patients).all()

    return templates.TemplateResponse(
        request=request,
        name="patients/list.html",
        context={"patients" : patients}
    )

# GET DELETE CONFIRMATION POPUP OF PATIENT
@views_router.get("/patients/{patient_id}/delete")
def get_patient_delete_popup(patient_id: int, request: Request, db: Session = Depends(get_db)):
    patient = patient_exist(patient_id, db)

    if not patient:
        return HTTPException(404, "Le patient n'existe pas")

    return templates.TemplateResponse(
        request=request,
        name="/patients/delete_confirm.html",
        context={"patient" : patient}
    )

# DELETE ONE PATIENT
# DELETE ON CASCADE FOR ALL FOREIGN KEYS
@views_router.delete("/patients/{patient_id}/delete")
async def delete_patient(patient_id: int, request: Request, db: Session = Depends(get_db)):
    patient = patient_exist(patient_id, db)

    if not patient:
        return HTTPException(404, "Le patient n'existe pas")
    
    #get all measurements + delete
    db.query(PatientMeasurement).filter(PatientMeasurement.patient_id == patient_id).delete()
    
    #get all comorbidities + delete
    comorbidities = db.query(PatientComorbidity).filter(PatientComorbidity.patient_id == patient_id).delete()
    
    #get all meal plan & foods related + delete
    meal_plans = db.query(MealPlan).filter(MealPlan.patient_id == patient_id).all()

    for plan in meal_plans:
        db.query(MealPlanFood).filter(MealPlanFood.plan_id == plan.id).delete()
    db.flush()

    for plan in meal_plans:
        db.delete(plan)
    db.flush()

    db.delete(patient)

    db.commit()

    patients = db.query(Patients).all()
    return templates.TemplateResponse(
        request=request,
        name="patients/list.html",
        context={"patients" : patients}
    )

##########################
### PATIENT MEAL PLANS ###
##########################

# GET MEAL PLAN'S FORM
@views_router.get("/patients/{patient_id}/meal_plans/new")
def new_meal_plans_form(patient_id: int, request: Request):
    return templates.TemplateResponse(
        request=request,
        name="patients/meal_plans_form.html",
        context={"patient_id" : patient_id}
    )

# POST NEW MEAL PLAN FOR A PATIENT
@views_router.post("/patients/{patient_id}/meal_plans/new")
async def create_new_meal_plan(patient_id: int, request: Request, meal_plan: MealPlanCreate = Depends(get_meal_plans_form), db: Session = Depends(get_db)):
    patient = db.query(Patients).filter(Patients.id == patient_id).first()
        
    if patient is None:
        return HTTPException(404, "Le patient n'existe pas")

    next_number = (
        db.query(func.max(MealPlan.number))
        .filter(MealPlan.patient_id == patient_id)
        .scalar() or 0
    ) + 1

    new_meal_plan = MealPlan(
        patient_id=patient_id, 
        start_date=date.today(),
        number=next_number,
        name=meal_plan.name,
        goal=meal_plan.goal)
    
    db.add(new_meal_plan)
    db.commit()

    meal_plans = get_patient_meal_plans(db, patient_id)

    return templates.TemplateResponse(
        request=request,
        name="patients/meal_plans_tab.html",
        context={"patient" : patient, "meal_plans" : meal_plans}
    )  

# DELETE A MEAL PLAN
@views_router.delete("/patients/{patient_id}/meal_plans/{meal_plan_id}")
async def delete_meal_plan(patient_id: int, meal_plan_id: int, request: Request, db: Session = Depends(get_db)):
    patient = db.query(Patients).filter(Patients.id == patient_id).first()
        
    if patient is None:
        return HTTPException(404, "Le patient n'existe pas")

    meal_plan = db.query(MealPlan).filter(MealPlan.id == meal_plan_id, MealPlan.patient_id == patient_id).first()

    if meal_plan is None:
        return HTTPException(404, "Le plan alimentaire n'existe pas")

    db.query(MealPlanFood).filter(MealPlanFood.plan_id == meal_plan_id).delete()
    db.delete(meal_plan)
    db.commit()

    meal_plans = get_patient_meal_plans(db, patient_id)

    return templates.TemplateResponse(
        request=request,
        name="patients/meal_plans_tab.html",
        context={"patient" : patient, "meal_plans" : meal_plans}
    )      


############################
#####  COMORBIDITIES   #####
############################

# GET COMORBIDITIES'S FORM
# LOAD PATIENT'S COMORBIDITIES TO SHOW ALREADY SELECTED ONE
# LOAD ALL COMORDITIES CHOICES
@views_router.get("/patients/{patient_id}/comorbidities/edit")
def manage_comorbidities(patient_id: int, request: Request, db: Session = Depends(get_db)):
    patient = db.query(Patients).filter(Patients.id == patient_id).first()
    
    if patient is None:
        return HTTPException(404, "Le patient n'existe pas")

    all_comorbidities = db.query(Comorbidities).all()

    patient_comorbidities = (
        db.query(PatientComorbidity)
        .filter(PatientComorbidity.patient_id == patient_id)
        .options(joinedload(PatientComorbidity.comorbidity))
        .all()
    )

    patient_comorbidities_ids = {c.comorbidity_id for c in patient_comorbidities}


    return templates.TemplateResponse(
        request=request,
        name="patients/comorbidities_form.html",
        context={"patient" : patient, "all_comorbidities" : all_comorbidities, "patient_comorbidities_ids" : patient_comorbidities_ids}
    )

# POST PATIENT'S COMORDITIES CHANGES
@views_router.post("/patients/{patient_id}/comorbidities/edit")
async def manage_comorbidities(patient_id: int, request: Request, db: Session = Depends(get_db), comorbidities_ids: List[int] = Form(default=[])):
    if not patient_exist(patient_id, db):
        return HTTPException(404, "Le patient n'existe pas")

    to_delete = (
        db.query(PatientComorbidity)
        .filter(PatientComorbidity.patient_id == patient_id)
        .all()
    )

    for item in to_delete:
        db.delete(item)
    db.commit()

    for comorbidity in comorbidities_ids:
        new_relation = PatientComorbidity(
            patient_id = patient_id,
            comorbidity_id = comorbidity
        )
        db.add(new_relation)
    
    db.commit()

    comorbidities = (
        db.query(PatientComorbidity)
        .filter(PatientComorbidity.patient_id == patient_id)
        .options(joinedload(PatientComorbidity.comorbidity))
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="patients/comorbidities_list.html",
        context={"comorbidities" : comorbidities}
    )


############################
######  MEASUREMENTS  ######
############################

# DELETE A PATIENT'S MEASURE
@views_router.delete("/patients/{patient_id}/measurements/{measure_id}")
async def delete_measurement(patient_id: int, measure_id: int, request: Request, db: Session = Depends(get_db)):
    patient = patient_exist(patient_id, db)
    if not patient:
        return HTTPException(404, "le patient n'existe pas")

    measure = (
        db.query(PatientMeasurement)
        .filter(PatientMeasurement.patient_id == patient_id)
        .filter(PatientMeasurement.id == measure_id)
        .first()
    )

    if not measure:
        return HTTPException(404, "La mesure n'existe pas")
    
    db.delete(measure)
    db.commit()

    measurements = db.query(PatientMeasurement).filter(PatientMeasurement.patient_id == patient_id).all()

    return templates.TemplateResponse(
        request=request,
        name="patients/measurements_tab.html",
        context={"patient" : patient, "measurements" : measurements}
    )

# GET MEASUREMENT'S FORM
@views_router.get("/patients/{patient_id}/measurements/new")
def new_measurement_form(patient_id: int, request: Request):
    return templates.TemplateResponse(
        request=request,
        name="patients/measurements_form.html",
        context={"patient_id" : patient_id, "measure" : None, "today" : date.today()}
    )

# GET MEASUREMENT'S FORM IN EDIT MODE
@views_router.get("/patients/{patient_id}/measurements/{measure_id}/edit")
def edit_measurement_form(patient_id: int, measure_id: int, request: Request, db: Session = Depends(get_db)):
    measure = db.query(PatientMeasurement).filter(PatientMeasurement.id == measure_id).first()

    if not measure:
        return HTTPException(404, "la mesure n'existe pas pour le patient sélectionné")

    return templates.TemplateResponse(
        request=request,
        name="patients/measurements_form.html",
        context={"patient_id" : patient_id, "measure" : measure}
    )

# POST NEW MEASURE FOR A PATIENT
@views_router.post("/patients/{patient_id}/measurements/new")
async def create_measurement(patient_id: int, request: Request, measure: PatientMeasurementCreate = Depends(get_measurement_form), db: Session = Depends(get_db)):
    patient = patient_exist(patient_id, db)
    if not patient:
        return HTTPException(404, "le patient n'existe pas")

    new_measure = PatientMeasurement(patient_id=patient_id, **measure.model_dump())
    db.add(new_measure)
    db.commit()
    
    measurements = db.query(PatientMeasurement).filter(PatientMeasurement.patient_id == patient_id).all()

    return templates.TemplateResponse(
        request=request,
        name="patients/measurements_tab.html",
        context={"patient" : patient, "measurements" : measurements}
    )

# PUT CHANGES FOR A MEASURE OF ONE PATIENT
@views_router.put("/patients/{patient_id}/measurements/{measure_id}/edit")
async def update_measurement(patient_id: int, measure_id: int, request: Request, measure: PatientMeasurementCreate = Depends(get_measurement_form), db: Session = Depends(get_db)):
    patient = patient_exist(patient_id, db)
    if not patient:
        return HTTPException(404, "Le patient n'existe pas")

    db.query(PatientMeasurement).filter(PatientMeasurement.id == measure_id).update(measure.model_dump())
    db.commit()

    measurements = db.query(PatientMeasurement).filter(PatientMeasurement.patient_id == patient_id).all()

    return templates.TemplateResponse(
        request=request,
        name="patients/measurements_tab.html",
        context={"patient": patient, "measurements": measurements}
    )

############################
######   MEAL PLAN   #######
############################

#GET MEAL PLAN DETAILS PAGE
@views_router.get("/meal_plans/{meal_plan_id}")
def get_meal_plan_details(meal_plan_id: int, request: Request, db: Session = Depends(get_db)):
    meal_plan = db.query(MealPlan).filter(MealPlan.id == meal_plan_id).first()

    if not meal_plan:
        return HTTPException(404, "Le plan alimentaire n'existe pas")
    
    patient = db.query(Patients).filter(Patients.id == meal_plan.patient_id).first()

    meal_plan_foods = (
        db.query(MealPlanFood)
        .filter(MealPlanFood.plan_id == meal_plan_id)
        .options(joinedload(MealPlanFood.food))
        .all()
    )

    foods, total = calculate_macro(meal_plan_foods)

    return templates.TemplateResponse(
        request=request,
        name="meal_plans/details.html",
        context={"patient" : patient, "plan" : meal_plan, "foods" : foods, "total" : total}
    )

# GET NEW FOOD FORM
@views_router.get("/meal_plans/{meal_plan_id}/foods/new")
def new_add_food_form(meal_plan_id: int, request: Request):
        return templates.TemplateResponse(
        request=request,
        name="meal_plans/foods_form.html",
        context={"meal_plan_id" : meal_plan_id}
    )

# GET FOOD NAME INPUT - SEARCH ENGINE
@views_router.get("/foods/search")
def search_foods(food_search: str = "", db: Session = Depends(get_db)):
    if len(food_search) < 2:
        return HTMLResponse("")
    
    foods = (
        db.query(Foods)
        .filter(Foods.name.ilike(f"%{food_search}%"))
        .order_by(
            case(
                (Foods.name.ilike(f"{food_search}%"), 0),
                else_=1
            ),
            Foods.name
        )
        .limit(100)
        .all()
    )
    
    html = ""
    for food in foods:
        html += f'<button type="button" class="list-group-item list-group-item-action" onclick="selectFood({food.id}, \'{food.name}\')">{food.name}</button>'
    
    return HTMLResponse(html)

# POST NEW FOOD INFORMATION INSIDE MEAL PLAN
@views_router.post("/meal_plans/{meal_plan_id}/foods/new")
async def add_food_to_mealplan(meal_plan_id: int, request: Request, food: MealPlanFoodCreate = Depends(get_food_form), db: Session = Depends(get_db)):
    meal_plan = db.query(MealPlan).filter(MealPlan.id == meal_plan_id).first()
    if not meal_plan:
        return HTTPException(404, "Le plan alimentaire n'existe pas")

    meal_plan_food = MealPlanFood(plan_id=meal_plan_id, **food.model_dump())
    
    db.add(meal_plan_food)
    db.commit()

    meal_plan_foods = (
        db.query(MealPlanFood)
        .filter(MealPlanFood.plan_id == meal_plan_id)
        .options(joinedload(MealPlanFood.food))
        .all()
    )

    foods, total = calculate_macro(meal_plan_foods)

    return templates.TemplateResponse(
        request=request,
        name="meal_plans/foods_table.html",
        context={"foods" : foods, "total" : total}
    )