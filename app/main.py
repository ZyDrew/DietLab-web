from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routes.patients import patients_router
from app.routes.recipes import recipes_router
from app.routes.foods import foods_router
from app.routes.comorbidities import comorbidities_router
from app.routes.meal_plan import meal_plan_router
from app.routes.views import views_router

app = FastAPI()

#Use to include the router for all HTML views
app.include_router(views_router)

#Use to include all the routes from the routers declaration - For API and tests only
app.include_router(patients_router, prefix="/api")
app.include_router(recipes_router, prefix="/api")
app.include_router(foods_router, prefix="/api")
app.include_router(comorbidities_router, prefix="/api")
app.include_router(meal_plan_router, prefix="/api")

#Use to include all static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")
