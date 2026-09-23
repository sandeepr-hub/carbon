from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.campus import Campus
from app.models.assessment import Assessment, AssessmentSummary

router = APIRouter(prefix="/api/benchmarks", tags=["Cross-Campus & Historical Benchmarks"])

@router.get("/campuses")
def compare_campuses(db: Session = Depends(get_db)):
    campuses = db.query(Campus).all()
    results = []
    for c in campuses:
        latest_asm = db.query(Assessment).filter(Assessment.campus_id == c.id).order_by(Assessment.reporting_year.desc()).first()
        summary = latest_asm.summary if latest_asm else None
        results.append({
            "campus_id": c.id,
            "name": c.name,
            "campus_type": c.campus_type,
            "population": c.population,
            "area_acres": c.area,
            "built_up_area_sqm": c.total_built_up_area_sqm,
            "reporting_year": latest_asm.reporting_year if latest_asm else None,
            "gross_tco2e": summary.gross_emissions if summary else 0.0,
            "reductions_tco2e": summary.eligible_reductions if summary else 0.0,
            "net_tco2e": summary.net_footprint if summary else 0.0,
            "tco2e_per_person": summary.gross_per_person if summary else 0.0,
            "net_tco2e_per_person": summary.net_per_person if summary else 0.0,
            "tco2e_per_sqm": summary.gross_per_area if summary else 0.0,
            "renewable_pct": summary.renewable_percentage if summary else 0.0
        })
    return results

@router.get("/historical")
def get_historical_trend(campus_id: int, db: Session = Depends(get_db)):
    assessments = db.query(Assessment).filter(Assessment.campus_id == campus_id).order_by(Assessment.reporting_year.asc()).all()
    history = []
    for a in assessments:
        s = a.summary
        history.append({
            "assessment_id": a.id,
            "year": a.reporting_year,
            "name": a.name,
            "scope1": s.scope1 if s else 0.0,
            "scope2": s.scope2 if s else 0.0,
            "scope3": s.scope3 if s else 0.0,
            "gross_tco2e": s.gross_emissions if s else 0.0,
            "reductions_tco2e": s.eligible_reductions if s else 0.0,
            "net_tco2e": s.net_footprint if s else 0.0,
            "tco2e_per_person": s.gross_per_person if s else 0.0
        })
    return history
