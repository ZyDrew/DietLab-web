from fastapi import Form
from app.schemas.login import LoginCreate

def get_login_form(
    email: str = Form(...),
    password: str = Form(...),
) -> LoginCreate:
    return LoginCreate(
        email=email,
        password=password
    )