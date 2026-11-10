
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


# Schema for receiving profile information
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


# Schema for sending profile information
class UserProfileResponse(UserProfileCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)
