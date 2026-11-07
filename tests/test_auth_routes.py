from app.models.user_sessions import UserSessions
from app.models.users import Users
from app.routes.auth import safe_next_url
from app.services.auth import hash_password
from tests.helpers import TEST_PASSWORD, session_for


def cookie_attributes(response):
    header = response.headers.get("set-cookie", "")
    return {part.strip().lower() for part in header.split(";")}


def test_login_page_renders_next(client):
    response = client.get("/login?next=/patients")

    assert response.status_code == 200
    assert 'name="next" value="/patients"' in response.text


def test_login_success_sets_session_cookie(client, user, db):
    response = client.post(
        "/login",
        data={"email": user.email, "password": TEST_PASSWORD},
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/"

    session = session_for(db, client)
    raw_token = client.cookies.get("dietlab_session")

    assert session is not None
    assert session.user_id == user.id
    assert session.token_hash != raw_token
    assert len(session.token_hash) == 64

    attrs = cookie_attributes(response)
    assert "httponly" in attrs
    assert "samesite=lax" in attrs
    assert "path=/" in attrs
    assert "max-age=604800" in attrs
    assert "secure" not in attrs


def test_login_wrong_password(client, user, db):
    response = client.post(
        "/login",
        data={"email": user.email, "password": "wrong-password"},
        follow_redirects=False,
    )

    assert response.status_code == 401
    assert "Email ou mot de passe incorrect." in response.text
    assert 'value="auth-fixture@example.com"' in response.text
    assert "wrong-password" not in response.text
    assert response.headers.get("set-cookie") is None
    assert session_for(db, client) is None


def test_login_unknown_email(client, db):
    response = client.post(
        "/login",
        data={"email": "unknown@example.com", "password": TEST_PASSWORD},
        follow_redirects=False,
    )

    assert response.status_code == 401
    assert "Email ou mot de passe incorrect." in response.text
    assert response.headers.get("set-cookie") is None
    assert session_for(db, client) is None


def test_login_inactive_user(client, db):
    inactive = Users(
        email="inactive@example.com",
        password_hash=hash_password(TEST_PASSWORD),
        is_active=False,
    )
    db.add(inactive)
    db.flush()

    response = client.post(
        "/login",
        data={"email": inactive.email, "password": TEST_PASSWORD},
        follow_redirects=False,
    )

    assert response.status_code == 401
    assert "Email ou mot de passe incorrect." in response.text
    assert response.headers.get("set-cookie") is None
    assert session_for(db, client) is None


def test_login_normalizes_email(client, user, db):
    response = client.post(
        "/login",
        data={"email": user.email.upper(), "password": TEST_PASSWORD},
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert session_for(db, client) is not None


def test_login_next_redirects(client, user):
    cases = [
        ("/patients", "/patients"),
        ("/patients?tab=measures", "/patients?tab=measures"),
        ("https://example.com", "/"),
        ("//example.com", "/"),
        ("///example.com", "/"),
        ("//[::1", "/"),
    ]

    for next_url, expected in cases:
        response = client.post(
            "/login",
            data={
                "email": user.email,
                "password": TEST_PASSWORD,
                "next": next_url,
            },
            follow_redirects=False,
        )

        assert response.status_code == 303
        assert response.headers["location"] == expected


def test_login_cookie_secure_flag(client, user, monkeypatch):
    monkeypatch.setattr("app.routes.auth.COOKIE_SECURE", True)

    response = client.post(
        "/login",
        data={"email": user.email, "password": TEST_PASSWORD},
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert "secure" in cookie_attributes(response)


def test_logout_revokes_session_and_clears_cookie(auth_client, db):
    session = session_for(db, auth_client)
    assert session is not None

    response = auth_client.post("/logout", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/login"
    assert db.query(UserSessions).filter(UserSessions.id == session.id).first() is None
    assert auth_client.cookies.get("dietlab_session") is None
    assert "max-age=0" in cookie_attributes(response)


def test_logout_without_session(client):
    response = client.post("/logout", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/login"
    assert client.cookies.get("dietlab_session") is None


def test_logout_with_stale_cookie(auth_client):
    for cookie in auth_client.cookies.jar:
        if cookie.name == "dietlab_session":
            cookie.value = "stale-token"

    response = auth_client.post("/logout", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/login"
    assert auth_client.cookies.get("dietlab_session") is None


def test_safe_next_url():
    assert safe_next_url("/patients") == "/patients"
    assert safe_next_url("/patients?tab=measures") == "/patients?tab=measures"
    assert safe_next_url("/patients/login-history") == "/patients/login-history"
    assert safe_next_url("/login") == "/"
    assert safe_next_url("/login/") == "/"
    assert safe_next_url("/logout") == "/"
    assert safe_next_url("https://example.com") == "/"
    assert safe_next_url("//example.com") == "/"
    assert safe_next_url("///example.com") == "/"
    assert safe_next_url("//[::1") == "/"
    assert safe_next_url("/\\example.com") == "/"
    assert safe_next_url("/patients\r\n") == "/"
    assert safe_next_url("/patients\x7f") == "/"
    assert safe_next_url("javascript:alert(1)") == "/"
    assert safe_next_url("patients") == "/"
    assert safe_next_url("") == "/"
