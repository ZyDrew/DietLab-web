from pwdlib import PasswordHash

from app.models.users import Users

password_hash = PasswordHash.recommended()
dummy_hash = password_hash.hash("dummypassword")

def hash_password(password):
    return password_hash.hash(password)

def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)

def normalize_email(email: str) -> str:
    return email.strip().lower()

def authenticate_user(db, email: str, password: str) -> Users | None:
    user = db.query(Users).filter(Users.email == normalize_email(email)).first()

    if not user:
        verify_password(password, dummy_hash)
        return None

    if not verify_password(password, user.password_hash):
        return None

    if not user.is_active:
        return None

    return user