import datetime

from app.models.user_sessions import UserSessions
from app.models.users import Users
from hashlib import sha256
from sqlalchemy import or_
import secrets

ABSOLUTE_TIMEOUT = datetime.timedelta(days=7)
IDLE_TIMEOUT = datetime.timedelta(hours=8)
TOUCH_INTERVAL = datetime.timedelta(minutes=5)

def _as_utc(now: datetime.datetime | None):
    if now is None:
        return datetime.datetime.now(datetime.timezone.utc)
    if now.tzinfo is None:
        raise ValueError("now must be timezone-aware")
    return now.astimezone(datetime.timezone.utc)

def hash_token(token):
    return sha256(token.encode("utf-8")).hexdigest()


def create_session(db, user_id: int, now=None) -> str:
    """
    Create user session in DB
    Store token hash only + CSRF Token
    Return raw token
    """
    now = _as_utc(now)
    raw_token = secrets.token_urlsafe(32)
    token_hash = hash_token(raw_token)

    created_at = now
    last_seen_at = now
    expires_at = now + ABSOLUTE_TIMEOUT

    csrf_token = secrets.token_urlsafe(32) 

    db.add(UserSessions(token_hash=token_hash, user_id=user_id, created_at=created_at, last_seen_at=last_seen_at, expires_at=expires_at, csrf_token=csrf_token))
    db.commit()
    return raw_token


def validate_session(db, token, now=None) -> Users | None:
    """
    Look up for active user and corresponding hashed token
    Touch last_seen_at if needed (every 5 minutes)
    Return user or None
    """
    now = _as_utc(now)
    token_hash = hash_token(token)
    user_session = db.query(UserSessions).filter(UserSessions.token_hash == token_hash).first()
    
    if not user_session:
        return None
    
    user = db.query(Users).filter(Users.id == user_session.user_id).first()
    if not user or not user.is_active:
        return None

    idle_cutoff = now - IDLE_TIMEOUT
    if user_session.expires_at <= now or user_session.last_seen_at <= idle_cutoff:
        return None

    if (now - user_session.last_seen_at) >= TOUCH_INTERVAL:
        user_session.last_seen_at = now
        db.commit()

    return user
        

def revoke_session(db, token) -> bool:
    """ Return if a row was deleted or not """
    token_hash = hash_token(token)
    count = db.query(UserSessions).filter(UserSessions.token_hash == token_hash).delete()
    
    if count > 0:
        db.commit()
    
    return count > 0


def revoke_user_sessions(db, user_id: int) -> int:
    """ Return total number of rows deleted """
    count = db.query(UserSessions).filter(UserSessions.user_id == user_id).delete()
    
    if count > 0:
        db.commit()
    
    return count


def purge_expired_sessions(db, now=None) -> int:
    """ Return total number of rows deleted """
    now = _as_utc(now)

    idle_cutoff = now - IDLE_TIMEOUT

    count = (
        db.query(UserSessions)
        .filter(or_(UserSessions.expires_at <= now, UserSessions.last_seen_at <= idle_cutoff))
        .delete()
    )
    
    if count > 0:
        db.commit()
    
    return count

def get_csrf_token(db, raw_session_token) -> str | None:
    token_hash = hash_token(raw_session_token)
    user_session = db.query(UserSessions).filter(UserSessions.token_hash == token_hash).first()

    if not user_session:
        return None

    if not user_session.csrf_token:
        csrf_token = secrets.token_urlsafe(32)
        user_session.csrf_token = csrf_token
        db.commit()

    return user_session.csrf_token