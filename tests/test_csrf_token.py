import json
import re

from app.models.patients import Patients
from app.models.user_sessions import UserSessions
from app.services.sessions import create_session, get_csrf_token, hash_token
from tests.helpers import make_patient


def test_csrf_missing_header(auth_client, db):
    patient = make_patient(db)

    response = auth_client.delete(f"/patients/{patient.id}/delete")

    assert response.status_code == 403
    assert db.query(Patients).filter(Patients.id == patient.id).first() is not None


def test_csrf_wrong_token(auth_client, db):
    patient = make_patient(db)

    response = auth_client.delete(
        f"/patients/{patient.id}/delete",
        headers={"X-CSRF-Token": "wrong-token"},
    )

    assert response.status_code == 403
    assert db.query(Patients).filter(Patients.id == patient.id).first() is not None


def test_csrf_valid_token(auth_client, db):
    patient = make_patient(db)
    token = get_csrf_token(db, auth_client.cookies.get("dietlab_session"))

    response = auth_client.delete(
        f"/patients/{patient.id}/delete",
        headers={"X-CSRF-Token": token},
    )

    assert response.status_code == 200
    assert db.query(Patients).filter(Patients.id == patient.id).first() is None


def test_csrf_token_from_another_session(auth_client, db, user):
    patient = make_patient(db)

    other_token = create_session(db, user.id)
    other_session = db.query(UserSessions).filter(UserSessions.token_hash == hash_token(other_token)).first()

    response = auth_client.delete(
        f"/patients/{patient.id}/delete",
        headers={"X-CSRF-Token": other_session.csrf_token},
    )

    assert response.status_code == 403
    assert db.query(Patients).filter(Patients.id == patient.id).first() is not None


def test_get_does_not_require_csrf(auth_client):
    response = auth_client.get("/patients")

    assert response.status_code == 200


def test_csrf_token_is_rendered_in_base_template(auth_client, db):
    response = auth_client.get("/")
    match = re.search(r"hx-headers='([^']+)'", response.text)

    assert match is not None
    headers = json.loads(match.group(1))
    assert headers["X-CSRF-Token"] == get_csrf_token(db, auth_client.cookies.get("dietlab_session"))
