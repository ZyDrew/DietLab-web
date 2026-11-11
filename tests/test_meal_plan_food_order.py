from datetime import date

from app.models.enums import MealPlanEnum
from app.models.meal_plan import MealPlan
from app.models.meal_plan_food import MealPlanFood
from tests.helpers import get_csrf_token, make_food, make_patient

# Business order of the periods, written out on purpose: the tests below are the
# specification, so they must not follow the constant they are meant to protect.
EXPECTED_PERIODS = [
    MealPlanEnum.BREAKFAST,
    MealPlanEnum.MORNING_SNACK,
    MealPlanEnum.LUNCH,
    MealPlanEnum.AFTERNOON_SNACK,
    MealPlanEnum.DINNER,
    MealPlanEnum.EVENING_SNACK,
]

# Every period once, in an order that is neither the business order nor alphabetical.
SHUFFLED_PERIODS = [
    MealPlanEnum.DINNER,
    MealPlanEnum.BREAKFAST,
    MealPlanEnum.EVENING_SNACK,
    MealPlanEnum.LUNCH,
    MealPlanEnum.AFTERNOON_SNACK,
    MealPlanEnum.MORNING_SNACK,
]

# The fragment test seeds every period but one, then adds the missing one through the form.
POSTED_PERIOD = MealPlanEnum.MORNING_SNACK
SEEDED_PERIODS = [period for period in SHUFFLED_PERIODS if period is not POSTED_PERIOD]


def build_plan(db, periods):
    """Create one patient, one plan and one food per period, in the given order."""
    patient = make_patient(db)
    plan = MealPlan(
        patient_id=patient.id,
        number=1,
        name="Plan sans libelle de periode",
        start_date=date.today(),
    )
    db.add(plan)
    db.flush()

    foods = [(make_food(f"Aliment {period.value}"), period) for period in periods]
    db.add_all([food for food, _ in foods])
    db.flush()

    for food, period in foods:
        db.add(MealPlanFood(
            plan_id=plan.id,
            food_id=food.id,
            quantity=100,
            frequency=7,
            period=period,
        ))
    db.flush()

    return plan


def assert_periods_in_order(text):
    """Each period label is rendered once, in the business order."""
    labels = [period.label for period in EXPECTED_PERIODS]

    missing = [label for label in labels if label not in text]
    assert missing == [], f"period labels not rendered: {missing}"

    positions = [text.index(label) for label in labels]
    assert positions == sorted(positions), f"periods out of order: {list(zip(labels, positions))}"


def test_meal_plan_page_orders_periods(auth_client, db):
    plan = build_plan(db, SHUFFLED_PERIODS)

    response = auth_client.get(f"/meal_plans/{plan.id}")

    assert response.status_code == 200
    assert_periods_in_order(response.text)


def test_meal_plan_fragment_after_add_orders_periods(auth_client, db):
    plan = build_plan(db, SEEDED_PERIODS)
    added_food = make_food("Aliment ajoute")
    db.add(added_food)
    db.flush()

    csrf_token = get_csrf_token(db, auth_client.cookies.get("dietlab_session"))

    response = auth_client.post(
        f"/meal_plans/{plan.id}/foods/new",
        data={
            "food_id": added_food.id,
            "quantity": 100,
            "frequency": 7,
            "period": POSTED_PERIOD.value,
        },
        headers={"X-CSRF-Token": csrf_token},
    )

    assert response.status_code == 200
    assert added_food.name in response.text
    assert_periods_in_order(response.text)
