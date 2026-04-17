from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.comorbidities import ComorbidityCreate, ComorbidityResponse
from app.models.comorbidities import Comorbidities

comorbidities_router = APIRouter(
    prefix="/comorbidities",
    tags=["comorbidities"]
)

# SELECT ALL comorbidities
@comorbidities_router.get("/", response_model=list[ComorbidityResponse])
def get_comorbidities(db: Session = Depends(get_db)):
    return db.query(Comorbidities).all()

# SELECT comorbidity BASE ON ID
@comorbidities_router.get("/{comorbidity_id}", response_model=ComorbidityResponse)
def get_comorbidity(comorbidity_id: int, db: Session = Depends(get_db)):
    comorbidity = db.query(Comorbidities).filter(Comorbidities.id == comorbidity_id).first()

    if comorbidity is None:
        raise HTTPException(404, "Comorbidité introuvable")
    
    return comorbidity

# INSERT NEW comorbidity
@comorbidities_router.post("/", response_model=ComorbidityResponse)
def create_comorbidity(comorbidity: ComorbidityCreate, db: Session = Depends(get_db)):
    #model_dump converts the comorbidityCreate object into a Python dictionnary. Allows to decompress into comorbidity's constructor
    new_comorbidity = Comorbidities(**comorbidity.model_dump())
    db.add(new_comorbidity)
    db.commit()
    #After commit, SQLAlchemy doesn't know the object ID create by the DB.
    #"refresh" forces SQLAlchemy to read the DB's object again and register the ID before returning the new created object
    db.refresh(new_comorbidity)
    return new_comorbidity


# MODIFY ONE comorbidity
@comorbidities_router.put("/{comorbidity_id}", response_model=ComorbidityResponse)
def modify_comorbidity(comorbidity_id: int, comorbidity: ComorbidityCreate, db: Session = Depends(get_db)):
    upd_comorbidity = db.query(Comorbidities).filter(Comorbidities.id == comorbidity_id).first()

    if upd_comorbidity is None:
        raise HTTPException(404, "Comorbidité à modifier, introuvable")
    
    db.query(Comorbidities).filter(Comorbidities.id == comorbidity_id).update(comorbidity.model_dump())
    db.commit()
    db.refresh(upd_comorbidity)

    return upd_comorbidity

# DELETE ONE comorbidity
@comorbidities_router.delete("/{comorbidity_id}", status_code=204)
def delete_comorbidity(comorbidity_id: int, db: Session = Depends(get_db)):
    comorbidity = db.query(Comorbidities).filter(Comorbidities.id == comorbidity_id).first()

    if comorbidity is None:
        raise HTTPException(404, "Comorbidité à supprimer, introuvable")
    
    db.delete(comorbidity)
    db.commit()

    return Response(status_code=204)
