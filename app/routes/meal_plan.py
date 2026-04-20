from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.meal_plan import MealPlanCreate, MealPlanResponse
from app.models.meal_plan import MealPlan
from app.schemas.meal_plan_food import MealPlanFoodCreate, MealPlanFoodResponse
from app.models.meal_plan_food import MealPlanFood

meal_plan_router = APIRouter(
    prefix="/meal_plan",
    tags=["meal_plan"]
)

# SELECT ALL MEAL_PLAN OF ONE PATIENT
@meal_plan_router.get("/patient/{patient_id}", response_model=list[MealPlanResponse])
def get_all_meal_plan(patient_id: int, db: Session = Depends(get_db)):
    return db.query(MealPlan).filter(MealPlan.patient_id == patient_id).all()

# SELECT MEAL_PLAN BASE ON ID
@meal_plan_router.get("/{meal_plan_id}", response_model=MealPlanResponse)
def get_meal_plan(meal_plan_id: int, db: Session = Depends(get_db)):
    meal_plan = db.query(MealPlan).filter(MealPlan.id == meal_plan_id).first()

    if meal_plan is None:
        raise HTTPException(404, "Plan alimentaire introuvable")
    
    return meal_plan

# INSERT NEW MEAL_PLAN
@meal_plan_router.post("/patient/{patient_id}", response_model=MealPlanResponse)
def create_meal_plan(patient_id: int, meal_plan: MealPlanCreate, db: Session = Depends(get_db)):
    new_meal_plan = MealPlan(
        patient_id = patient_id,
        **meal_plan.model_dump()
    )

    db.add(new_meal_plan)
    db.commit()

    db.refresh(new_meal_plan)
    return new_meal_plan

# MODIFY ONE MEAL_PLAN -> NOT USEFULL
"""
@meal_plan_router.put("/{meal_plan_id}", response_model=MealPlanResponse)
def modify_meal_plan(meal_plan_id: int, meal_plan: MealPlanCreate, db: Session = Depends(get_db)):
    upd_meal_plan = db.query(MealPlan).filter(MealPlan.id == meal_plan_id).first()

    if upd_meal_plan is None:
        raise HTTPException(404, "Plan alimentaire à modifier, introuvable")
    
    db.query(MealPlan).filter(MealPlan.id == meal_plan_id).update(meal_plan.model_dump())
    db.commit()
    db.refresh(upd_meal_plan)

    return upd_meal_plan
"""

# DELETE ONE MEAL_PLAN
@meal_plan_router.delete("/{meal_plan_id}", status_code=204)
def delete_meal_plan(meal_plan_id: int, db: Session = Depends(get_db)):
    meal_plan = db.query(MealPlan).filter(MealPlan.id == meal_plan_id).first()

    if meal_plan is None:
        raise HTTPException(404, "Plan alimentaire à supprimer, introuvable")
    
    db.delete(meal_plan)
    db.commit()

    return Response(status_code=204)

# ADD ONE FOOD TO MEAL_PLAN
@meal_plan_router.post("/{meal_plan_id}/foods", response_model=MealPlanFoodResponse)
def add_food_to_plan(meal_plan_id: int, food_in: MealPlanFoodCreate, db: Session = Depends(get_db)):
    meal_plan = db.query(MealPlan).filter(MealPlan.id == meal_plan_id).first()

    if meal_plan is None:
        raise HTTPException(404, "Plan alimentaire, introuvable")

    new_relation = MealPlanFood(
        plan_id = meal_plan_id,
        **food_in.model_dump()
    )

    db.add(new_relation)
    db.commit()
    db.refresh(new_relation)

    return new_relation

# DELETE ONE FOOD OF MEAL_PLAN
@meal_plan_router.delete("/{meal_plan_id}/{food_id}", status_code=204)
def delete_food_from_plan(meal_plan_id: int, food_id: int, db: Session = Depends(get_db)):
    relation = (
        db.query(MealPlanFood)
        .filter(MealPlanFood.id == meal_plan_id) 
        .filter(MealPlanFood.food_id == food_id)
        .first()
    )

    if relation is None:
        raise HTTPException(404, "La relation PlanAlimentaire - Aliment n'existe pas")

    db.delete(relation)
    db.commit()

    return Response(status_code=204)

# MODIFY ONE FOOD OF MEAL_PLAN
@meal_plan_router.put("/{meal_plan_id}/foods", response_model=MealPlanFoodResponse)
def update_food_from_plan(meal_plan_id: int, food_in: MealPlanFoodCreate, db: Session = Depends(get_db)):
    upd_food = (
        db.query(MealPlanFood)
        .filter(MealPlanFood.plan_id == meal_plan_id)
        .filter(MealPlanFood.food_id == food_in.food_id)
        .first()
    )

    if upd_food is None:
        raise HTTPException(404, "L'aliment à modifier de ce plan n'existe pas")
    
    db.query(MealPlanFood).filter(MealPlanFood.plan_id == meal_plan_id and MealPlanFood.food_id == food_in.food_id).update(food_in.model_dump())
    db.commit()
    db.refresh(upd_food)

    return upd_food