import uuid
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserRegistrationForm(BaseModel):
    fullname: str = Field(..., min_length=1, max_length=100, description="Full name of the user")
    email: EmailStr = Field(..., description="Valid email address")
    password: str = Field(..., min_length=8, max_length=128, description="Password (8-128 characters)")

    @field_validator("fullname")
    @classmethod
    def validate_fullname(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Fullname must not be empty or whitespace only.")
        return v

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()


UserRegisterRequest = UserRegistrationForm


class UserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    fullname: str
    is_active: bool
    is_admin: bool

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: str | None = None
    email: str | None = None