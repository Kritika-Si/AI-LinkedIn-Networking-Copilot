
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

    # Get the latest saved profile
    profile = db.query(UserProfile).order_by(
        UserProfile.id.desc()
    ).first()

    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Please save your profile before generating recommendations."
        )

    # Generate recommendations
    recommendations = generate_recommendations(
        profile.linkedin_profile,
        profile.career_goals or ""
    )

    return {
        "message": "Recommendations generated successfully",
        "profile_id": profile.id,
        "total_recommendations": len(recommendations),
        "recommendations": recommendations
    }
