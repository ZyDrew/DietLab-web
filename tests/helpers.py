import datetime

from app.models.enums import GenderEnum
from app.models.foods import Foods
from app.models.patients import Patients
from app.models.user_sessions import UserSessions
from app.services.sessions import hash_token

TEST_PASSWORD = "correct-password"


def make_food(name: str) -> Foods:
    return Foods(name=name, calories=0, proteins=0, fat=0, carbs=0,
                 calcium=0, iron=0, vitamin_c=0)

def make_patient(db):
    patient = Patients(
        lastname="Doe",
        firstname="Jane",
        gender=GenderEnum.FEMALE,
        birthdate=datetime.date(1975, 10, 25),
    )
    db.add(patient)
    db.flush()
    return patient

def get_csrf_token(db, session_token):
    session = db.query(UserSessions).filter(UserSessions.token_hash == hash_token(session_token)).first()
    return session.csrf_token


def session_for(db, client):
    session_token = client.cookies.get("dietlab_session")
    if session_token is None:
        return None
    return db.query(UserSessions).filter(UserSessions.token_hash == hash_token(session_token)).first()