from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import UserProfile
from schemas import UserProfileCreate, UserProfileResponse


router = APIRouter(
    prefix="/api/profiles",
    tags=["Profiles"]
)


# Create a new profile
@router.post("/", response_model=UserProfileResponse)
def create_profile(
    profile: UserProfileCreate,
    db: Session = Depends(get_db)
):
    new_profile = UserProfile(**profile.model_dump())

    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)

    return new_profile


# Get all profiles
@router.get("/", response_model=list[UserProfileResponse])
def get_profiles(db: Session = Depends(get_db)):
    return db.query(UserProfile).all()


# Get a profile by ID
@router.get("/{profile_id}", response_model=UserProfileResponse)
def get_profile(profile_id: int, db: Session = Depends(get_db)):
    profile = db.query(UserProfile).filter(
        UserProfile.id == profile_id
    ).first()

    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )

    return profile


# Update a profile
@router.put("/{profile_id}", response_model=UserProfileResponse)
def update_profile(
    profile_id: int,
    updated_data: UserProfileCreate,
    db: Session = Depends(get_db)
):
    profile = db.query(UserProfile).filter(
        UserProfile.id == profile_id
    ).first()

    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )

    for key, value in updated_data.model_dump().items():
        setattr(profile, key, value)

    db.commit()
    db.refresh(profile)

    return profile


# Delete a profile
@router.delete("/{profile_id}")
def delete_profile(profile_id: int, db: Session = Depends(get_db)):
    profile = db.query(UserProfile).filter(
        UserProfile.id == profile_id
    ).first()

    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )

    db.delete(profile)
    db.commit()

    return {
        "message": "Profile deleted successfully"
    }