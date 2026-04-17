from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.meal_plan import MealPlanCreate, MealPlanResponse
from app.models.meal_plan import MealPlan

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

# DELETE ONE meal_plan
@meal_plan_router.delete("/{meal_plan_id}", status_code=204)
def delete_meal_plan(meal_plan_id: int, db: Session = Depends(get_db)):
    meal_plan = db.query(MealPlan).filter(MealPlan.id == meal_plan_id).first()

    if meal_plan is None:
        raise HTTPException(404, "Plan alimentaire à supprimer, introuvable")
    
    db.delete(meal_plan)
    db.commit()

    return Response(status_code=204)
