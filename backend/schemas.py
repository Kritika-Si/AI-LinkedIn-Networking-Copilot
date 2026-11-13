
from typing import Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
)


# Authentication schemas
class UserRegister(BaseModel):
    full_name: str = Field(min_length=2, max_length=150)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Full name cannot be empty")
        return value

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()


class AuthUserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


# Existing profile schemas
class UserProfileCreate(BaseModel):
    full_name: Optional[str] = Field(default=None, max_length=150)
    headline: Optional[str] = Field(default=None, max_length=250)

    linkedin_profile: str = Field(
        min_length=1,
        max_length=10000
    )

    skills: Optional[str] = Field(default=None, max_length=2000)
    education: Optional[str] = Field(default=None, max_length=3000)
    experience: Optional[str] = Field(default=None, max_length=5000)

    career_goals: Optional[str] = Field(default=None, max_length=3000)
    preferred_roles: Optional[str] = Field(default=None, max_length=250)

    @field_validator("linkedin_profile")
    @classmethod
    def validate_linkedin_profile(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("LinkedIn profile cannot be empty")

        return value


class UserProfileResponse(UserProfileCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)
