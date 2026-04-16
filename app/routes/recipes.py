from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.recipes import RecipeResponse, RecipeCreate
from app.models.recipes import Recipes

recipes_router = APIRouter(
    prefix="/recipes",
    tags=["recipes"]
)

# SELECT ALL RECIPES
@recipes_router.get("/", response_model=list[RecipeResponse])
def get_recipes(db: Session = Depends(get_db)):
    return db.query(Recipes).all()

# SELECT RECIPE BASE ON ID
@recipes_router.get("/{recipe_id}", response_model=RecipeResponse)
def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    recipe = db.query(Recipes).filter(Recipes.id == recipe_id).first()

    if recipe is None:
        raise HTTPException(404, "Recette introuvable")
    
    return recipe

# INSERT NEW RECIPE
@recipes_router.post("/", response_model=RecipeResponse)
def create_recipe(recipe: RecipeCreate, db: Session = Depends(get_db)):
    #model_dump converts the RecipeCreate object into a Python dictionnary. Allows to decompress into recipe's constructor
    new_recipe = Recipes(**recipe.model_dump())
    db.add(new_recipe)
    db.commit()
    #After commit, SQLAlchemy doesn't know the object ID create by the DB.
    #"refresh" forces SQLAlchemy to read the DB's object again and register the ID before returning the new created object
    db.refresh(new_recipe)
    return new_recipe


# MODIFY ONE RECIPE
@recipes_router.put("/{recipe_id}", response_model=RecipeResponse)
def modify_recipe(recipe_id: int, recipe: RecipeCreate, db: Session = Depends(get_db)):
    upd_recipe = db.query(Recipes).filter(Recipes.id == recipe_id).first()

    if upd_recipe is None:
        raise HTTPException(404, "Recette à modifier, introuvable")
    
    db.query(Recipes).filter(Recipes.id == recipe_id).update(recipe.model_dump())
    db.commit()
    db.refresh(upd_recipe)

    return upd_recipe

# DELETE ONE RECIPE
@recipes_router.delete("/{recipe_id}", status_code=204)
def delete_recipe(recipe_id: int, db: Session = Depends(get_db)):
    recipe = db.query(Recipes).filter(Recipes.id == recipe_id).first()

    if recipe is None:
        raise HTTPException(404, "Recette à supprimer, introuvable")
    
    db.delete(recipe)
    db.commit()

    return Response(status_code=204)
