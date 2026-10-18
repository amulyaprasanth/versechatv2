import os
import uuid
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from fastapi import HTTPException, status
import jwt
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from versechat_backend.models.db import User

load_dotenv()
load_dotenv(".env.dev")

SECRET_KEY = os.getenv("SECRET_KEY", "temporary-fallback-secret-key-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

password_hash = PasswordHash.recommended()
DUMMY_HASH = password_hash.hash("random-password")


def hash_password(password: str) -> str:
    """Returns hashed password."""
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """Returns True if password is correct."""
    return password_hash.verify(password, hashed_password)


def get_user(session: Session, email: str) -> User | None:
    """Return the user matching the normalized email, or None if not found."""
    normalized_email = email.strip().lower()
    stmt = select(User).where(User.email == normalized_email)
    return session.scalars(stmt).one_or_none()


def get_user_by_id(session: Session, user_id: uuid.UUID | str) -> User | None:
    """Return the user matching the ID, or None if not found."""
    if isinstance(user_id, str):
        try:
            user_id = uuid.UUID(user_id)
        except (ValueError, AttributeError):
            return None
    stmt = select(User).where(User.id == user_id)
    return session.scalars(stmt).one_or_none()


def add_user(
    session: Session,
    email: str,
    password: str,
    fullname: str,
) -> User:
    """Create a user with a hashed password."""
    normalized_email = email.strip().lower()
    clean_fullname = fullname.strip()

    if get_user(session, normalized_email) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    new_user = User(
        email=normalized_email,
        password_hash=hash_password(password),
        fullname=clean_fullname,
    )

    try:
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return new_user

    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        ) from exc
    except Exception:
        session.rollback()
        raise


def authenticate_user(session: Session, email: str, password: str) -> User | None:
    """Authenticates the user using email and password."""
    normalized_email = email.strip().lower()
    user = get_user(session, normalized_email)

    if not user:
        verify_password(password, DUMMY_HASH)
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Creates a JWT token from data with UTC expiration."""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=15)
    to_encode.update({"exp": expire, "iat": now})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

    