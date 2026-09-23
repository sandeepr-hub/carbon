from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.engine.recommendation_engine import generate_campus_recommendations

router = APIRouter(prefix="/api/recommendations", tags=["Hotspots & Recommendations"])

@router.get("/")
def get_recommendations(assessment_id: int, db: Session = Depends(get_db)):
    return generate_campus_recommendations(db, assessment_id)
