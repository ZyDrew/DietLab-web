"""
Administrative CLI

Run:
    python -m app.cli create-user
    python -m app.cli set-password <email>
"""
import argparse
import getpass
import re
import sys

from sqlalchemy.exc import IntegrityError

from app.database import SessionLocal
from app.models.users import Users
from app.models.user_sessions import UserSessions
from app.services.auth import hash_password, normalize_email

MIN_PASSWORD_LENGTH = 12
EMAIL_PATTERN = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")


def prompt_password() -> str:
    password = getpass.getpass("Password: ")
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError(
            f"Password must be at least {MIN_PASSWORD_LENGTH} characters."
        )

    confirmation = getpass.getpass("Confirm password: ")
    if password != confirmation:
        raise ValueError("Passwords do not match.")

    return password


def prompt_email() -> str:
    email = normalize_email(input("Email: "))
    if not EMAIL_PATTERN.fullmatch(email):
        raise ValueError("Invalid email address.")
    return email


def create_user(_args: argparse.Namespace) -> int:
    db = SessionLocal()
    try:
        email = prompt_email()

        if db.query(Users).filter(Users.email == email).first():
            print(f"User {email} already exists.")
            return 1

        password = prompt_password()
        db.add(Users(email=email, password_hash=hash_password(password)))
        db.commit()
        print(f"User {email} created.")
        return 0

    except IntegrityError:
        db.rollback()
        print(f"User {email} already exists.")
        return 1
    except (ValueError, EOFError) as exc:
        db.rollback()
        print(f"Aborted: {exc}")
        return 1
    except KeyboardInterrupt:
        db.rollback()
        print("\nAborted.")
        return 1
    finally:
        db.close()


def set_password(args: argparse.Namespace) -> int:
    db = SessionLocal()
    try:
        email = normalize_email(args.email)
        user = db.query(Users).filter(Users.email == email).first()

        if user is None:
            print(f"User {email} not found.")
            return 1

        user.password_hash = hash_password(prompt_password())
        db.query(UserSessions).filter(UserSessions.user_id == user.id).delete()
        db.commit()
        print(f"Password updated for {email}. All sessions were revoked.")
        return 0

    except (ValueError, EOFError) as exc:
        db.rollback()
        print(f"Aborted: {exc}")
        return 1
    except KeyboardInterrupt:
        db.rollback()
        print("\nAborted.")
        return 1
    finally:
        db.close()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="DietLab administration commands.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    create = subparsers.add_parser("create-user", help="Create a user account.")
    create.set_defaults(func=create_user)

    reset = subparsers.add_parser(
        "set-password", help="Change a user's password and revoke their sessions."
    )
    reset.add_argument("email", help="Email address of the user.")
    reset.set_defaults(func=set_password)

    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
