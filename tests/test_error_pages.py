import logging
from html import unescape
from urllib.parse import parse_qs, urlsplit

from fastapi.testclient import TestClient

from app.main import app
from app.models.patients import Patients
from tests.helpers import make_patient


def _raise_server_error():
    raise RuntimeError("boom-secret")


def test_missing_patient_returns_404_page(auth_client):
    response = auth_client.get("/patients/999999")
    body = unescape(response.text)

    assert response.status_code == 404
    assert "Le patient n'existe pas" in body
    assert "Retour à l'accueil" in body


def test_missing_patient_htmx_redirects_to_error_page(auth_client):
    response = auth_client.get(
        "/patients/999999",
        headers={"HX-Request": "true"},
    )

    assert response.status_code == 404
    location = response.headers["HX-Redirect"]
    parts = urlsplit(location)
    message = parse_qs(parts.query)["message"][0]

    assert parts.path == "/error/404"
    assert message == "Le patient n'existe pas"


def test_unknown_url_returns_404_page(client):
    response = client.get("/does-not-exist")

    assert response.status_code == 404
    assert "La page demandée est introuvable." in response.text


def test_error_routes_are_public(client):
    response = client.get("/error/403")
    body = unescape(response.text)
    assert response.status_code == 403
    assert "Vous n'avez pas accès à cette ressource." in body

    response = client.get("/error/404?message=Test")
    assert response.status_code == 404
    assert "Test" in response.text

    response = client.get("/error/500")
    assert response.status_code == 500
    assert "Une erreur est survenue." in response.text


def test_csrf_failure_returns_403_page(auth_client, db):
    patient = make_patient(db)

    response = auth_client.delete(f"/patients/{patient.id}/delete")
    body = unescape(response.text)

    assert response.status_code == 403
    assert "Accès refusé" in body
    assert "La requête n'a pas pu être vérifiée." in body
    assert db.query(Patients).filter(Patients.id == patient.id).first() is not None


def test_csrf_failure_htmx_redirects_to_error_page(auth_client, db):
    patient = make_patient(db)

    response = auth_client.delete(
        f"/patients/{patient.id}/delete",
        headers={"HX-Request": "true"},
    )

    assert response.status_code == 403
    location = response.headers["HX-Redirect"]
    parts = urlsplit(location)
    message = parse_qs(parts.query)["message"][0]

    assert parts.path == "/error/403"
    assert message == "La requête n'a pas pu être vérifiée. Rechargez la page et réessayez."
    assert db.query(Patients).filter(Patients.id == patient.id).first() is not None


def test_api_404_stays_json(auth_client):
    response = auth_client.get("/api/patients/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Patient introuvable"


def test_unhandled_exception_returns_500_page(caplog):
    app.add_api_route("/__test_500", _raise_server_error)
    app.add_api_route("/api/__test_500", _raise_server_error)

    try:
        client = TestClient(app, raise_server_exceptions=False)

        with caplog.at_level(logging.ERROR, logger="dietlab.errors"):
            response = client.get("/__test_500")

        assert response.status_code == 500
        assert "Une erreur est survenue." in response.text
        assert "boom-secret" not in response.text
        assert "/__test_500" in caplog.text
        assert "boom-secret" not in caplog.text

        response = client.get("/__test_500", headers={"HX-Request": "true"})
        assert response.status_code == 500
        assert response.headers["HX-Redirect"] == "/error/500"

        response = client.get("/api/__test_500")
        assert response.status_code == 500
        assert response.json()["detail"] == "Internal server error"
    finally:
        app.router.routes = [
            route
            for route in app.router.routes
            if getattr(route, "path", None) not in ("/__test_500", "/api/__test_500")
        ]
