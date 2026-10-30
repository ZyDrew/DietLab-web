import datetime

from app.models.user_sessions import UserSessions
from app.models.users import Users
from app.services.sessions import hash_token


def test_anonymous_html(client):
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 303

def test_anonymous_htmx(client):
    response = client.get("/", headers={"HX-Request": "true", "HX-Current-URL": "http://testserver/"}, follow_redirects=False)
    assert response.status_code == 401
    assert response.headers.get("HX-Redirect") == "/login?next=%2F"

def test_anonymous_api(client):
    response = client.get("/api/patients")
    assert response.status_code == 401
    assert response.headers["content-type"].startswith("application/json")
    assert response.json() == {"detail": "Not authenticated"}

def test_authenticated(auth_client):
    response = auth_client.get("/")
    assert response.status_code == 200
    response = auth_client.get("/api/patients")
    assert response.status_code == 200

def test_expired_session(auth_client, db):
    user_sessions = db.query(UserSessions).filter(UserSessions.token_hash == hash_token(auth_client.cookies.get("dietlab_session"))).first()
    user_sessions.expires_at = datetime.datetime(2026, 10, 26, 10, 0, tzinfo=datetime.timezone.utc)
    db.commit()
    response = auth_client.get("/", headers={"HX-Request": "true", "HX-Current-URL": "/patients"}, follow_redirects=False)
    assert response.status_code == 401
    assert response.headers.get("HX-Redirect") == "/login?next=%2Fpatients"

def test_inactive_user(auth_client, user, db):
    user.is_active = False
    db.commit()
    response = auth_client.get("/", follow_redirects=False)
    assert response.status_code == 303