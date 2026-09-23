from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.assessment import Assessment, AssessmentSummary
from app.models.campus import Campus
from app.schemas.schemas import AssessmentCreate, AssessmentOut
from app.engine.carbon_calculator import calculate_gross_emissions
from app.engine.reduction_calculator import calculate_reduction_contributions
from app.engine.aggregator import aggregate_assessment_summary

router = APIRouter(prefix="/api/assessments", tags=["Assessments"])

@router.get("/", response_model=list[AssessmentOut])
def list_assessments(campus_id: int = None, db: Session = Depends(get_db)):
    query = db.query(Assessment)
    if campus_id:
        query = query.filter(Assessment.campus_id == campus_id)
    return query.all()

@router.get("/{assessment_id}", response_model=AssessmentOut)
def get_assessment(assessment_id: int, db: Session = Depends(get_db)):
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return assessment

@router.post("/", response_model=AssessmentOut)
def create_assessment(asm_in: AssessmentCreate, db: Session = Depends(get_db)):
    campus = db.query(Campus).filter(Campus.id == asm_in.campus_id).first()
    if not campus:
        raise HTTPException(status_code=404, detail="Campus not found")

    asm = Assessment(
        campus_id=asm_in.campus_id,
        name=asm_in.name,
        reporting_year=asm_in.reporting_year,
        start_date=asm_in.start_date,
        end_date=asm_in.end_date,
        status="Draft",
        methodology=asm_in.methodology,
        boundary_description=asm_in.boundary_description
    )
    db.add(asm)
    db.flush()

    # Initialize empty summary
    summary = AssessmentSummary(
        assessment_id=asm.id,
        population=campus.population,
        built_up_area_sqm=campus.total_built_up_area_sqm
    )
    db.add(summary)
    db.commit()
    db.refresh(asm)
    return asm

@router.post("/{assessment_id}/calculate")
def trigger_full_calculation(assessment_id: int, db: Session = Depends(get_db)):
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    calcs = calculate_gross_emissions(db, assessment_id)
    reductions = calculate_reduction_contributions(db, assessment_id)
    summary = aggregate_assessment_summary(db, assessment_id)

    assessment.status = "Completed"
    db.commit()

    return {
        "success": True,
        "assessment_id": assessment_id,
        "calculations_count": len(calcs),
        "reductions_count": len(reductions),
        "gross_emissions_tco2e": summary.gross_emissions if summary else 0.0,
        "eligible_reductions_tco2e": summary.eligible_reductions if summary else 0.0,
        "net_footprint_tco2e": summary.net_footprint if summary else 0.0
    }
