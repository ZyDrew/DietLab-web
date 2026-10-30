from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.users import Users
from app.services.sessions import validate_session
from app.errors import NotAuthenticated


def get_current_user(request: Request, db: Session = Depends(get_db)) -> Users | None:
    token = request.cookies.get("dietlab_session")
    if token is None:
        raise NotAuthenticated()
    
    user = validate_session(db, token)
    if user is None:
        raise NotAuthenticated()
    else:
        request.state.user = user
        return user
    