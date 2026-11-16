from app.services.foods import SEARCH_LIMIT, search_foods
from tests.helpers import make_food


def test_term_shorter_than_the_minimum_returns_nothing(db):
    db.add(make_food("zqriz"))
    db.flush()

    assert search_foods(db, "") == []
    assert search_foods(db, "  ") == []
    assert search_foods(db, "%") == []


def test_percent_is_matched_literally(db):
    db.add_all([make_food("zqjus 100%"), make_food("zqjus 1000 ml")])
    db.flush()

    names = [food.name for food in search_foods(db, "zqjus 100%")]

    assert names == ["zqjus 100%"]


def test_underscore_is_matched_literally(db):
    db.add_all([make_food("zqfilet_o"), make_food("zqfiletto")])
    db.flush()

    names = [food.name for food in search_foods(db, "zqfilet_o")]

    assert names == ["zqfilet_o"]


def test_backslash_is_matched_literally(db):
    db.add_all([make_food("zqdir C:\\repas"), make_food("zqdir CXrepas")])
    db.flush()

    names = [food.name for food in search_foods(db, "zqdir C:\\")]

    assert names == ["zqdir C:\\repas"]


def test_wildcard_only_term_does_not_match_every_row(db):
    db.add(make_food("zqsel"))
    db.flush()

    names = [food.name for food in search_foods(db, "%%")]

    assert "zqsel" not in names


def test_prefix_matches_come_first_and_search_ignores_case(db):
    db.add_all([make_food("zqtomate"), make_food("Sauce zqtomate")])
    db.flush()

    names = [food.name for food in search_foods(db, "ZQTOMATE")]

    assert names.index("zqtomate") < names.index("Sauce zqtomate")


def test_results_are_limited(db):
    db.add_all([make_food(f"zqlimite {index}") for index in range(SEARCH_LIMIT + 5)])
    db.flush()

    assert len(search_foods(db, "zqlimite")) == SEARCH_LIMIT


def test_plain_term_matches_an_accented_name(db):
    db.add(make_food("ZqPâté de campagne"))
    db.flush()

    names = [food.name for food in search_foods(db, "zqpate")]

    assert names == ["ZqPâté de campagne"]


def test_accented_term_matches_a_plain_name(db):
    db.add(make_food("ZqPate de campagne"))
    db.flush()

    names = [food.name for food in search_foods(db, "zqpâté")]

    assert names == ["ZqPate de campagne"]


def test_prefix_order_ignores_accents(db):
    db.add_all([make_food("ZqPate"), make_food("Sauce zqpate")])
    db.flush()

    names = [food.name for food in search_foods(db, "zqpâté")]

    assert names.index("ZqPate") < names.index("Sauce zqpate")
