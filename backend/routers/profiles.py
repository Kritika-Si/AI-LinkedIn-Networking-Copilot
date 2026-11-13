
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import User, UserProfile
from schemas import UserProfileCreate, UserProfileResponse
from dependencies import get_current_user


router = APIRouter(
    prefix="/api/profiles",
    tags=["Profiles"]
)


# Create a profile for the logged-in user
@router.post("/", response_model=UserProfileResponse)
def create_profile(
    profile: UserProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_profile = UserProfile(
        **profile.model_dump(),
        user_id=current_user.id,
    )

    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)

    return new_profile


# Get only the logged-in user's profiles
@router.get("/", response_model=list[UserProfileResponse])
def get_profiles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(UserProfile)
        .filter(UserProfile.user_id == current_user.id)
        .all()
    )


# Get a profile only if it belongs to the logged-in user
@router.get("/{profile_id}", response_model=UserProfileResponse)
def get_profile(
    profile_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = (
        db.query(UserProfile)
        .filter(
            UserProfile.id == profile_id,
            UserProfile.user_id == current_user.id,
        )
        .first()
    )

    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Profile not found",
        )

    return profile


# Update only the logged-in user's profile
@router.put("/{profile_id}", response_model=UserProfileResponse)
def update_profile(
    profile_id: int,
    updated_data: UserProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = (
        db.query(UserProfile)
        .filter(
            UserProfile.id == profile_id,
            UserProfile.user_id == current_user.id,
        )
        .first()
    )

    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Profile not found",
        )

    for key, value in updated_data.model_dump().items():
        setattr(profile, key, value)

    db.commit()
    db.refresh(profile)

    return profile


# Delete only the logged-in user's profile
@router.delete("/{profile_id}")
def delete_profile(
    profile_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = (
        db.query(UserProfile)
        .filter(
            UserProfile.id == profile_id,
            UserProfile.user_id == current_user.id,
        )
        .first()
    )

    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Profile not found",
        )

    db.delete(profile)
    db.commit()

    return {
        "message": "Profile deleted successfully"
    }
