import hashlib
import json
import secrets
import uuid
from base64 import urlsafe_b64encode
from datetime import UTC, datetime, timedelta
from typing import Annotated, Any, cast

import jwt
from cryptography.fernet import Fernet, InvalidToken
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from sqlalchemy import delete, select, text, update
from sqlalchemy.engine import CursorResult
from sqlalchemy.orm import Session

from versechat_backend.database import get_db
from versechat_backend.models.auth import (
    Token,
    UserRegistrationForm,
    UserResponse,
)
from versechat_backend.models.db import RefreshToken, RefreshTokenRotation, User
from versechat_backend.utils import (
    ALGORITHM,
    SECRET_KEY,
    add_user,
    authenticate_user,
    create_access_token,
    get_user_by_id,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

ACCESS_TOKEN_EXPIRY_MINUTES = 30
REFRESH_TOKEN_LIFETIME = timedelta(days=30)
REFRESH_ROTATION_GRACE = timedelta(seconds=15)

# Derive a separate encryption key from the application's stable signing secret.
_rotation_cipher = Fernet(
    urlsafe_b64encode(
        hashlib.sha256(f"versechat-refresh-rotation:{SECRET_KEY}".encode()).digest()
    )
)


class RefreshRequest(BaseModel):
    refresh_token: str = Field(..., min_length=32, max_length=256)


def _get_grace_response(
    session: Session,
    token_hash: str,
    family_id: uuid.UUID,
    now: datetime,
) -> Token | None:
    rotation = session.scalar(
        select(RefreshTokenRotation).where(
            RefreshTokenRotation.token_hash == token_hash,
            RefreshTokenRotation.family_id == family_id,
        )
    )
    if rotation is None:
        return None

    grace_expires_at = rotation.grace_expires_at
    if grace_expires_at.tzinfo is None:
        grace_expires_at = grace_expires_at.replace(tzinfo=UTC)
    if grace_expires_at <= now:
        return None

    try:
        payload = _rotation_cipher.decrypt(rotation.encrypted_tokens.encode("utf-8"))
        return Token.model_validate(json.loads(payload))
    except InvalidToken, ValueError, TypeError:
        return None


def _revoke_refresh_family(
    session: Session, family_id: uuid.UUID, now: datetime
) -> None:
    session.execute(
        update(RefreshToken)
        .where(
            RefreshToken.family_id == family_id,
            RefreshToken.revoked_at.is_(None),
        )
        .values(revoked_at=now)
    )
    session.execute(
        delete(RefreshTokenRotation).where(RefreshTokenRotation.family_id == family_id)
    )
    session.commit()


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[Session, Depends(get_db)],
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
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token expired",
        )
    except jwt.PyJWTError:
        raise credentials_exception

    sub = payload.get("sub")
    if not isinstance(sub, str):
        raise credentials_exception

    try:
        user_id = uuid.UUID(sub)
    except ValueError:
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
    session: Annotated[Session, Depends(get_db)],
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
    summary="Obtain JWT access token (Login)",
)
async def get_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[Session, Depends(get_db)],
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
    refresh_token = secrets.token_urlsafe(48)
    refresh_token_hash = hashlib.sha256(refresh_token.encode("utf-8")).hexdigest()

    token_obj = RefreshToken(
        user_id=user.id,
        token_hash=refresh_token_hash,
        family_id=uuid.uuid4(),
        expires_at=datetime.now(UTC) + REFRESH_TOKEN_LIFETIME,
    )

    session.add(token_obj)
    session.commit()

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRY_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=access_token_expires,
    )

    return Token(
        access_token=access_token, refresh_token=refresh_token, token_type="bearer"
    )


@router.post(
    "/refresh",
    summary="Rotate refresh token and issue a new access token",
)
async def refresh_tokens(
    request: RefreshRequest,
    session: Annotated[Session, Depends(get_db)],
) -> Token:
    # The app currently uses SQLite, which does not implement SELECT FOR UPDATE.
    # Acquire its write lock before reading so simultaneous refreshes serialize:
    # the second request then sees the first rotation and replays its cached pair.
    if session.get_bind().dialect.name == "sqlite":
        session.execute(text("BEGIN IMMEDIATE"))

    invalid_refresh = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired refresh token",
    )

    now = datetime.now(UTC)
    # Keep only replay responses that can still serve a concurrent request.
    session.execute(
        delete(RefreshTokenRotation).where(RefreshTokenRotation.grace_expires_at <= now)
    )
    presented_hash = hashlib.sha256(request.refresh_token.encode("utf-8")).hexdigest()
    current = session.scalar(
        select(RefreshToken)
        .where(RefreshToken.token_hash == presented_hash)
        .with_for_update()
    )
    if current is None:
        raise invalid_refresh

    if current.revoked_at is not None:
        grace_response = _get_grace_response(
            session, presented_hash, current.family_id, now
        )
        if grace_response is not None:
            return grace_response

        # A rotated token was used again. Revoke every still-active token in
        # this login session so a stolen token cannot keep the session alive.
        _revoke_refresh_family(session, current.family_id, now)
        raise invalid_refresh

    expires_at = current.expires_at
    # SQLite may return timezone-aware DateTime columns as naive values.
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=UTC)
    if expires_at <= now:
        raise invalid_refresh

    user = get_user_by_id(session, current.user_id)
    if user is None or not user.is_active:
        _revoke_refresh_family(session, current.family_id, now)
        raise invalid_refresh

    # Conditional update makes only one concurrent refresh request succeed.
    # A second use is treated as reuse and revokes the token family.
    rotation = cast(
        CursorResult[Any],
        session.execute(
            update(RefreshToken)
            .where(
                RefreshToken.id == current.id,
                RefreshToken.revoked_at.is_(None),
            )
            .values(revoked_at=now)
        ),
    )
    if rotation.rowcount != 1:
        grace_response = _get_grace_response(
            session, presented_hash, current.family_id, now
        )
        if grace_response is not None:
            return grace_response

        _revoke_refresh_family(session, current.family_id, now)
        raise invalid_refresh

    new_refresh_token = secrets.token_urlsafe(48)
    replacement = RefreshToken(
        user_id=user.id,
        token_hash=hashlib.sha256(new_refresh_token.encode("utf-8")).hexdigest(),
        family_id=current.family_id,
        expires_at=now + REFRESH_TOKEN_LIFETIME,
    )
    new_access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRY_MINUTES),
    )

    tokens = Token(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
    )
    replay_response = _rotation_cipher.encrypt(
        json.dumps(tokens.model_dump()).encode("utf-8")
    ).decode("utf-8")

    session.add(replacement)
    session.add(
        RefreshTokenRotation(
            token_hash=presented_hash,
            family_id=current.family_id,
            encrypted_tokens=replay_response,
            grace_expires_at=now + REFRESH_ROTATION_GRACE,
        )
    )
    session.commit()

    return tokens


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: RefreshRequest,
    session: Annotated[Session, Depends(get_db)],
) -> Response:
    """Revoke the refresh-token family represented by the supplied token."""
    presented_hash = hashlib.sha256(request.refresh_token.encode("utf-8")).hexdigest()
    current = session.scalar(
        select(RefreshToken).where(RefreshToken.token_hash == presented_hash)
    )

    if current is not None:
        now = datetime.now(UTC)
        session.execute(
            update(RefreshToken)
            .where(
                RefreshToken.family_id == current.family_id,
                RefreshToken.revoked_at.is_(None),
            )
            .values(revoked_at=now)
        )
        session.execute(
            delete(RefreshTokenRotation).where(
                RefreshTokenRotation.family_id == current.family_id
            )
        )
        session.commit()

    # Idempotent logout: callers don't learn whether a token was recognized.
    return Response(status_code=status.HTTP_204_NO_CONTENT)


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
