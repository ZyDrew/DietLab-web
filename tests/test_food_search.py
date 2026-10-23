from tests.helpers import make_food

def test_food_search_does_not_return_raw_html(client, db):
    db.add(make_food("<script>alert(1)</script>"))
    db.flush()

    response = client.get("/foods/search", params={"food_search": "<script>"})

    assert "<script>" not in response.text

def test_food_search_escapes_apostrophe(client, db):
    db.add(make_food("Huile d'olive"))
    db.flush()

    response = client.get("/foods/search", params={"food_search": "huile"})

    assert 'data-food-name="Huile d&#39;olive"' in response.text
    assert "onclick" not in response.text