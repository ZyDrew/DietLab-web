import secrets

from fastapi import Depends, Form, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.errors import CSRFError
from app.models.users import Users
from app.services.sessions import get_csrf_token, validate_session

SAFE_METHODS = ("GET", "HEAD", "OPTIONS")


def _compare_token(request: Request, provided: str | None) -> None:
    expected = getattr(request.state, "csrf_token", None)

    if not expected or not provided or not secrets.compare_digest(provided, expected):
        raise CSRFError()


def require_csrf(request: Request, current_user: Users = Depends(get_current_user)) -> None:
    if request.method in SAFE_METHODS:
        return

    _compare_token(request, request.headers.get("X-CSRF-Token"))


def require_logout_csrf(
    request: Request,
    csrf_token: str | None = Form(None),
    db: Session = Depends(get_db),
) -> None:
    """
    Protect logout with CSRF without requiring a session.

    An anonymous or stale-session logout changes nothing, so it stays a
    no-op redirect. A valid session must send the token either in the
    X-CSRF-Token header or in the form field.
    """
    if request.method in SAFE_METHODS:
        return

    session_token = request.cookies.get("dietlab_session")
    if session_token is None:
        return

    if validate_session(db, session_token) is None:
        return

    expected = get_csrf_token(db, session_token)
    provided = request.headers.get("X-CSRF-Token") or csrf_token

    if not expected or not provided or not secrets.compare_digest(provided, expected):
        raise CSRFError()
