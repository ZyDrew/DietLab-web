from fastapi import FastAPI
from app.routes.patients import patients_router

app = FastAPI()

#Use to include all the routes from the patients_router declaration
app.include_router(patients_router)

@app.get("/")
def home():
    return {"message" : "Hello World !"}

