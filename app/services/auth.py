from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()
dummy_hash = password_hash.hash("dummypassword")

def hash_password(password):
    return password_hash.hash(password)

def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)

def normalize_email(email: str) -> str:
    return email.strip().lower()