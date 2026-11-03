from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.users import Users
from app.services.sessions import get_csrf_token, validate_session
from app.errors import NotAuthenticated


def get_current_user(request: Request, db: Session = Depends(get_db)) -> Users:
    token = request.cookies.get("dietlab_session")
    if token is None:
        raise NotAuthenticated()
    
    user = validate_session(db, token)
    if user is None:
        raise NotAuthenticated()
    
    request.state.user = user
    csrf_token = get_csrf_token(db, token)
    request.state.csrf_token = csrf_token
    return user
    