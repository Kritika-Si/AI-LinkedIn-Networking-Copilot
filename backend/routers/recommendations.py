
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import UserProfile
from services.recommendation_engine import generate_recommendations


router = APIRouter(
    prefix="/api/recommendations",
    tags=["Recommendations"]
)


@router.get("/")
def get_recommendations(db: Session = Depends(get_db)):

    # Get the latest saved user profile
    profile = db.query(UserProfile).order_by(
        UserProfile.id.desc()
    ).first()

    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Please save your profile before generating recommendations."
        )

    # Get profile information from the database
    profile_text = profile.linkedin_profile or ""
    career_goals = profile.career_goals or ""
    preferred_roles = profile.preferred_roles or ""

    # Generate personalized recommendations
    recommendations = generate_recommendations(
        profile_text=profile_text,
        career_goals=career_goals,
        preferred_roles=preferred_roles
    )

    return {
        "message": "Recommendations generated successfully",
        "profile_id": profile.id,
        "total_recommendations": len(recommendations),
        "recommendations": recommendations
    }
