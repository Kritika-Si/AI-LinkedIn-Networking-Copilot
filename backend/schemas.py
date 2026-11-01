from pydantic import BaseModel, ConfigDict
from typing import Optional


# Schema for receiving profile information
class UserProfileCreate(BaseModel):
    full_name: Optional[str] = None
    headline: Optional[str] = None

    linkedin_profile: str

    skills: Optional[str] = None
    education: Optional[str] = None
    experience: Optional[str] = None

    career_goals: Optional[str] = None
    preferred_roles: Optional[str] = None


# Schema for sending profile information
class UserProfileResponse(UserProfileCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)