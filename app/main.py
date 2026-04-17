from fastapi import FastAPI
from app.routes.patients import patients_router
from app.routes.recipes import recipes_router
from app.routes.foods import foods_router
from app.routes.comorbidities import comorbidities_router
from app.routes.meal_plan import meal_plan_router

app = FastAPI()

#Use to include all the routes from the routers declaration
app.include_router(patients_router)
app.include_router(recipes_router)
app.include_router(foods_router)
app.include_router(comorbidities_router)
app.include_router(meal_plan_router)

@app.get("/")
def home():
    return {"message" : "Hello World !"}

