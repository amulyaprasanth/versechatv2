import uuid
from datetime import timedelta
from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from versechat_backend.database import get_db
from versechat_backend.models.auth import Token, UserRegistrationForm, UserResponse
from versechat_backend.models.db import User
from versechat_backend.utils import (
    ALGORITHM,
    SECRET_KEY,
    add_user,
    authenticate_user,
    create_access_token,
    get_user,
    get_user_by_id,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

ACCESS_TOKEN_EXPIRY_MINUTES = 30


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        sub = payload.get("sub")
        if not isinstance(sub, str):
            raise credentials_exception

        user_id = uuid.UUID(sub)

    except jwt.PyJWTError, ValueError:
        raise credentials_exception

    user = get_user_by_id(session, user_id)

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account",
        )

    return user


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register_user(
    user_data: UserRegistrationForm,
    session: Session = Depends(get_db),
) -> User:
    """
    Registers a new user account.
    - Validates email and password requirements.
    - Hashes password using Argon2id.
    - Returns sanitized UserResponse without exposing sensitive fields.
    """
    user = add_user(
        session=session,
        email=user_data.email,
        password=user_data.password,
        fullname=user_data.fullname,
    )
    return user


@router.post(
    "/token",
    response_model=Token,
    summary="Obtain JWT access token (Login)",
)
async def get_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Session = Depends(get_db),
) -> Token:
    """
    Authenticates a user via OAuth2 password flow and returns a JWT access token.
    - Protects against timing attacks with constant-time dummy verification.
    - Verifies user exists, password is correct, and account is active.
    """
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account",
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRY_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token, token_type="bearer")


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
)
async def get_current_user_profile(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Returns the profile of the currently authenticated user."""
    return current_user

