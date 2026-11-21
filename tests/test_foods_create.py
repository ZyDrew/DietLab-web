from app.models.foods import Foods
from tests.helpers import get_csrf_token

# Zq prefix keeps test rows distinct from Ciqual data in the shared database

VALID_FORM = {
    "name": "Zq Pudding maison",
    "calories": "250",
    "proteins": "5",
    "fat": "10",
    "carbs": "30",
    "calcium": "120",
    "iron": "1.2",
    "vitamin_c": "0.5",
}


def htmx_headers(auth_client, db):
    return {
        "X-CSRF-Token": get_csrf_token(db, auth_client.cookies.get("dietlab_session")),
        "HX-Request": "true",
    }


def test_new_food_form_renders(auth_client):
    response = auth_client.get("/foods/new")

    assert response.status_code == 200
    assert 'hx-post="/foods/new"' in response.text
    assert 'id="form-errors"' in response.text


def test_create_food_redirects_to_the_new_food(auth_client, db):
    response = auth_client.post("/foods/new", data=VALID_FORM, headers=htmx_headers(auth_client, db))

    food = db.query(Foods).filter(Foods.name == "Zq Pudding maison").one()

    assert response.status_code == 200
    assert response.headers["HX-Redirect"] == f"/foods/{food.id}"
    assert food.source == "MAN"


def test_duplicate_name_is_refused(auth_client, db):
    auth_client.post("/foods/new", data=VALID_FORM, headers=htmx_headers(auth_client, db))

    response = auth_client.post(
        "/foods/new",
        data={**VALID_FORM, "name": "  zq PUDDING maison  "},
        headers=htmx_headers(auth_client, db),
    )

    assert response.status_code == 422
    assert "existe déjà" in response.text
    assert db.query(Foods).filter(Foods.name.ilike("Zq Pudding maison")).count() == 1


def test_invalid_nutrient_shows_the_error_fragment(auth_client, db):
    response = auth_client.post(
        "/foods/new",
        data={**VALID_FORM, "calories": "-1"},
        headers=htmx_headers(auth_client, db),
    )

    assert response.status_code == 422
    assert response.headers["HX-Retarget"] == "#form-errors"
    assert "la valeur minimale" in response.text
    assert db.query(Foods).filter(Foods.name == "Zq Pudding maison").count() == 0
