import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.database import engine, get_db
from app.main import app
from app.models.users import Users
from app.services.auth import hash_password

TEST_PASSWORD = "correct-password"

@pytest.fixture
def db():
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint")

    def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield session
    finally:
        app.dependency_overrides.clear()
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def client(db):
    return TestClient(app)

@pytest.fixture
def user(db):
    user = Users(
        email="auth-fixture@example.com",
        password_hash=hash_password(TEST_PASSWORD)
    )
    db.add(user)
    db.flush()
    return user

@pytest.fixture
def auth_client(client, user):
    response = client.post(
        "/login",
        data={"email": user.email, "password": TEST_PASSWORD},
        follow_redirects=False
    )
    assert response.status_code == 303
    return client