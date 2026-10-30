import os
from urllib.parse import urlsplit

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.login_form import get_login_form
from app.schemas.login import LoginCreate
from app.services.auth import authenticate_user
from app.services.sessions import create_session, revoke_session
from app.templating import templates


auth_router = APIRouter()
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"
BLOCKED_PATHS = {"/login", "/logout"}

def safe_next_url(next_url: str) -> str:
    if not next_url or not next_url.startswith("/") or next_url.startswith("//"):
        return "/"

    if "\\" in next_url or any(ord(c) < 32 or ord(c) == 127 for c in next_url):
        return "/"

    try:
        parts = urlsplit(next_url)
    except ValueError:
        return "/"

    if parts.scheme or parts.netloc:
        return "/"

    if parts.path.rstrip("/") in BLOCKED_PATHS:
        return "/"

    return next_url

@auth_router.get("/login")
def get_login_page(request: Request):
    return templates.TemplateResponse(
          request=request,
          name="auth/login.html",
          context={"next": request.query_params.get("next", "/")}
    )


@auth_router.post("/login")
def post_login_form(request: Request, next: str = Form("/"), login: LoginCreate = Depends(get_login_form), db: Session = Depends(get_db)):
    user = authenticate_user(db, login.email, login.password)

    if not user:
        return templates.TemplateResponse(
        request=request,
        name="auth/login.html",
        context={
            "error": "Email ou mot de passe incorrect.", 
            "email": login.email, 
            "next": next
        },
        status_code=401
    )

    raw_token = create_session(db, user.id)
    response = RedirectResponse(url=safe_next_url(next), status_code=303)
    response.set_cookie(key="dietlab_session", value=raw_token, max_age=604800, httponly=True, samesite="lax", secure=COOKIE_SECURE, path="/")
    return response

@auth_router.post("/logout")
def post_logout(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("dietlab_session")
    if token:
        revoke_session(db, token)

    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie(key="dietlab_session", path="/")

    return response
