from app.models.foods import Foods
from tests.helpers import make_food

# Zq prefix keeps test rows distinct from Ciqual data in the shared database


def test_foods_page_shows_the_search_bar(auth_client):
    response = auth_client.get("/foods")

    assert response.status_code == 200
    assert 'hx-get="/foods/search?as_links=true"' in response.text
    assert "Recherchez un aliment" in response.text


def test_search_returns_links_on_the_page(auth_client, db):
    food = make_food("Zq Link test")
    db.add(food)
    db.flush()

    response = auth_client.get("/foods/search", params={"food_search": "zq lien", "as_links": "true"})

    assert response.status_code == 200
    assert f'<a href="/foods/{food.id}"' in response.text
    assert "data-food-id" not in response.text


def test_search_returns_buttons_for_the_modal(auth_client, db):
    food = make_food("Zq Bouton test")
    db.add(food)
    db.flush()

    response = auth_client.get("/foods/search", params={"food_search": "zq bouton"})

    assert f'data-food-id="{food.id}"' in response.text
    assert "<a href=" not in response.text


def test_food_details_page_shows_the_values(auth_client, db):
    food = Foods(
        name="Zq Détail test",
        calories=123,
        proteins=4.5,
        fat=2,
        carbs=20,
        calcium=30,
        iron=1,
        vitamin_c=0,
    )
    db.add(food)
    db.flush()
    db.refresh(food)

    response = auth_client.get(f"/foods/{food.id}")

    assert response.status_code == 200
    assert "Zq Détail test" in response.text
    assert "123.00" in response.text
    assert "100 g ou 100 ml" in response.text


def test_unknown_food_returns_404(auth_client):
    response = auth_client.get("/foods/999999")

    assert response.status_code == 404


def test_food_name_is_escaped_on_the_page(auth_client, db):
    food = make_food("<script>alert(1)</script>")
    db.add(food)
    db.flush()

    response = auth_client.get(f"/foods/{food.id}")

    assert "&lt;script&gt;" in response.text
    assert "<script>alert(1)</script>" not in response.text
