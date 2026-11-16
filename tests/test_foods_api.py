import pytest

VALID_FOOD = {
    "name": "Riz complet",
    "calories": 350,
    "proteins": 7.5,
    "fat": 1,
    "carbs": 75,
    "calcium": 10,
    "iron": 1.5,
    "vitamin_c": 0,
}

NUTRIENTS = ["calories", "proteins", "fat", "carbs", "calcium", "iron", "vitamin_c"]


def post_food(client, **overrides):
    return client.post("/api/foods/", json={**VALID_FOOD, **overrides})


def test_create_food_returns_200(auth_client):
    response = post_food(auth_client)

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Riz complet"
    assert body["source"] == "MAN"


@pytest.mark.parametrize("nutrient", NUTRIENTS)
def test_negative_nutrient_returns_422(auth_client, nutrient):
    response = post_food(auth_client, **{nutrient: -1})

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", nutrient]


def test_name_longer_than_300_characters_returns_422(auth_client):
    response = post_food(auth_client, name="a" * 301)

    assert response.status_code == 422


def test_name_of_only_spaces_returns_422(auth_client):
    response = post_food(auth_client, name="   ")

    assert response.status_code == 422
