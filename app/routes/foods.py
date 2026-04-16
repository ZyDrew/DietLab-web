from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.foods import FoodCreate, FoodResponse
from app.models.foods import Foods

foods_router = APIRouter(
    prefix="/foods",
    tags=["foods"]
)

# SELECT ALL foods
@foods_router.get("/", response_model=list[FoodResponse])
def get_foods(db: Session = Depends(get_db)):
    return db.query(Foods).all()

# SELECT food BASE ON ID
@foods_router.get("/{food_id}", response_model=FoodResponse)
def get_food(food_id: int, db: Session = Depends(get_db)):
    food = db.query(Foods).filter(Foods.id == food_id).first()

    if food is None:
        raise HTTPException(404, "Aliment introuvable")
    
    return food

# INSERT NEW food
@foods_router.post("/", response_model=FoodResponse)
def create_food(food: FoodCreate, db: Session = Depends(get_db)):
    #model_dump converts the foodCreate object into a Python dictionnary. Allows to decompress into food's constructor
    new_food = Foods(**food.model_dump())
    db.add(new_food)
    db.commit()
    #After commit, SQLAlchemy doesn't know the object ID create by the DB.
    #"refresh" forces SQLAlchemy to read the DB's object again and register the ID before returning the new created object
    db.refresh(new_food)
    return new_food


# MODIFY ONE food
@foods_router.put("/{food_id}", response_model=FoodResponse)
def modify_food(food_id: int, food: FoodCreate, db: Session = Depends(get_db)):
    upd_food = db.query(Foods).filter(Foods.id == food_id).first()

    if upd_food is None:
        raise HTTPException(404, "Aliment à modifier, introuvable")
    
    db.query(Foods).filter(Foods.id == food_id).update(food.model_dump())
    db.commit()
    db.refresh(upd_food)

    return upd_food

# DELETE ONE food
@foods_router.delete("/{food_id}", status_code=204)
def delete_food(food_id: int, db: Session = Depends(get_db)):
    food = db.query(Foods).filter(Foods.id == food_id).first()

    if food is None:
        raise HTTPException(404, "Aliment à supprimer, introuvable")
    
    db.delete(food)
    db.commit()

    return Response(status_code=204)
