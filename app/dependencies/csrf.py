import secrets

from fastapi import Depends, Request

from app.dependencies.auth import get_current_user
from app.errors import CSRFError
from app.models.users import Users


def require_csrf(request: Request, current_user: Users = Depends(get_current_user)) -> None:
    if request.method in ("GET", "HEAD", "OPTIONS"):
        return

    expected = getattr(request.state, "csrf_token", None)
    provided = request.headers.get("X-CSRF-Token")

    if not expected or not provided:
        raise CSRFError()

    if not secrets.compare_digest(provided, expected):
        raise CSRFError()