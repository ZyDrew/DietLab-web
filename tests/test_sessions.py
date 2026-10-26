import datetime

import pytest

from app.models.user_sessions import UserSessions
from app.models.users import Users
from app.services.sessions import (
    create_session,
    hash_token,
    purge_expired_sessions,
    revoke_session,
    revoke_user_sessions,
    validate_session,
)

t0 = datetime.datetime(2026, 10, 26, 10, 0, tzinfo=datetime.timezone.utc)
t0_plus_7d = t0 + datetime.timedelta(days=7)
t0_plus_9h = t0 + datetime.timedelta(hours=9)
t0_plus_1h = t0 + datetime.timedelta(hours=1)
t0_plus_4m = t0 + datetime.timedelta(minutes=4)
t0_plus_5m = t0 + datetime.timedelta(minutes=5)
t0_plus_7h = t0 + datetime.timedelta(hours=7)
t0_plus_8h = t0 + datetime.timedelta(hours=8)
t0_plus_14h = t0 + datetime.timedelta(hours=14)
t0_plus_22h = t0 + datetime.timedelta(hours=22)
t0_plus_7d_minus_30m = t0_plus_7d - datetime.timedelta(minutes=30)
t0_plus_7d_minus_1s = t0_plus_7d - datetime.timedelta(seconds=1)
t0_minus_1s = t0 - datetime.timedelta(seconds=1)
t0_minus_9h = t0 - datetime.timedelta(hours=9)

def test_create_session(db):
    user = Users(email="test@example.com", password_hash="dummyhash")
    db.add(user)
    db.flush()

    token_one = create_session(db, user.id, now=t0)
    token_two = create_session(db, user.id, now=t0)

    token_hash_one = hash_token(token_one)
    user_session = db.query(UserSessions).filter(UserSessions.token_hash == token_hash_one).first()

    assert token_one != token_two
    assert user_session is not None
    assert user_session.user_id == user.id
    assert user_session.token_hash == token_hash_one
    assert user_session.token_hash != token_one
    assert len(user_session.token_hash) == 64
    assert user_session.created_at == t0
    assert user_session.last_seen_at == t0
    assert user_session.expires_at == t0_plus_7d
    with pytest.raises(ValueError):
        create_session(db, user.id, datetime.datetime(2026, 10, 26))

def test_validate_session(db):
    user = Users(email="validate@example.com", password_hash="dummyhash")
    db.add(user)
    db.flush()

    token = create_session(db, user.id, now=t0)

    validated_user = validate_session(db, token, now=t0)

    assert validated_user is not None
    assert validated_user.id == user.id
    assert validate_session(db, "unknown-token", now=t0) is None


def test_validate_session_inactive_user(db):
    user = Users(email="inactive@example.com", password_hash="dummyhash", is_active=False)
    db.add(user)
    db.flush()

    token = create_session(db, user.id, now=t0)

    assert validate_session(db, token, now=t0) is None


def test_validate_session_idle_expiry(db):
    user = Users(email="idle@example.com", password_hash="dummyhash")
    db.add(user)
    db.flush()

    token = create_session(db, user.id, now=t0)

    assert validate_session(db, token, now=t0_plus_8h) is None
    assert validate_session(db, token, now=t0_plus_9h) is None


def test_validate_session_touch(db):
    user = Users(email="touch@example.com", password_hash="dummyhash")
    db.add(user)
    db.flush()

    token = create_session(db, user.id, now=t0)

    assert validate_session(db, token, now=t0_plus_4m) is not None
    db.expire_all()
    user_session = db.query(UserSessions).filter(UserSessions.token_hash == hash_token(token)).first()
    assert user_session.last_seen_at == t0

    assert validate_session(db, token, now=t0_plus_5m) is not None
    db.expire_all()
    user_session = db.query(UserSessions).filter(UserSessions.token_hash == hash_token(token)).first()
    assert user_session.last_seen_at == t0_plus_5m


def test_validate_session_sliding_idle(db):
    user = Users(email="sliding@example.com", password_hash="dummyhash")
    db.add(user)
    db.flush()

    token = create_session(db, user.id, now=t0)

    assert validate_session(db, token, now=t0_plus_7h) is not None
    assert validate_session(db, token, now=t0_plus_14h) is not None
    assert validate_session(db, token, now=t0_plus_22h) is None


def test_validate_session_absolute_cap(db):
    user = Users(email="absolute@example.com", password_hash="dummyhash")
    db.add(user)
    db.flush()

    token = create_session(db, user.id, now=t0)
    user_session = db.query(UserSessions).filter(UserSessions.token_hash == hash_token(token)).first()
    user_session.last_seen_at = t0_plus_7d_minus_30m
    db.commit()

    assert validate_session(db, token, now=t0_plus_7d_minus_1s) is not None
    assert validate_session(db, token, now=t0_plus_7d) is None


def test_revoke_session(db):
    user = Users(email="revoke@example.com", password_hash="dummyhash")
    db.add(user)
    db.flush()

    token_one = create_session(db, user.id, now=t0)
    token_two = create_session(db, user.id, now=t0)

    assert revoke_session(db, token_one) is True
    assert validate_session(db, token_one, now=t0) is None
    assert validate_session(db, token_two, now=t0) is not None
    assert revoke_session(db, "unknown-token") is False


def test_revoke_user_sessions(db):
    user_one = Users(email="user-one@example.com", password_hash="dummyhash")
    user_two = Users(email="user-two@example.com", password_hash="dummyhash")
    db.add_all([user_one, user_two])
    db.flush()

    token_one = create_session(db, user_one.id, now=t0)
    token_two = create_session(db, user_two.id, now=t0)

    count = revoke_user_sessions(db, user_one.id)

    assert count == 1
    assert validate_session(db, token_one, now=t0) is None
    assert validate_session(db, token_two, now=t0) is not None
    assert revoke_user_sessions(db, user_one.id) == 0


def test_purge_expired_sessions(db):
    user = Users(email="purge@example.com", password_hash="dummyhash")
    db.add(user)
    db.flush()

    token_absolute = create_session(db, user.id, now=t0)
    token_idle = create_session(db, user.id, now=t0)
    token_valid = create_session(db, user.id, now=t0)

    absolute_session = db.query(UserSessions).filter(UserSessions.token_hash == hash_token(token_absolute)).first()
    absolute_session.expires_at = t0_minus_1s
    absolute_session.last_seen_at = t0

    idle_session = db.query(UserSessions).filter(UserSessions.token_hash == hash_token(token_idle)).first()
    idle_session.last_seen_at = t0_minus_9h
    idle_session.expires_at = t0_plus_7d

    db.commit()

    count = purge_expired_sessions(db, now=t0_plus_1h)

    assert count == 2
    assert validate_session(db, token_absolute, now=t0_plus_1h) is None
    assert validate_session(db, token_idle, now=t0_plus_1h) is None
    assert validate_session(db, token_valid, now=t0_plus_1h) is not None
    assert purge_expired_sessions(db, now=t0_plus_1h) == 0