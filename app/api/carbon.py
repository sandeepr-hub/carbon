from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.carbon import CarbonCalculation, CarbonReductionContribution
from app.schemas.schemas import CarbonCalculationOut, CarbonReductionContributionOut
from app.engine.aggregator import get_building_wise_results, get_source_breakdown

router = APIRouter(prefix="/api/carbon", tags=["Carbon Accounting Engine"])

@router.get("/calculations", response_model=list[CarbonCalculationOut])
def list_calculations(assessment_id: int, db: Session = Depends(get_db)):
    return db.query(CarbonCalculation).filter(CarbonCalculation.assessment_id == assessment_id).all()

@router.get("/reductions", response_model=list[CarbonReductionContributionOut])
def list_reductions(assessment_id: int, db: Session = Depends(get_db)):
    return db.query(CarbonReductionContribution).filter(CarbonReductionContribution.assessment_id == assessment_id).all()

@router.get("/building-wise")
def get_buildings_breakdown(assessment_id: int, db: Session = Depends(get_db)):
    return get_building_wise_results(db, assessment_id)

@router.get("/source-wise")
def get_sources_breakdown(assessment_id: int, db: Session = Depends(get_db)):
    return get_source_breakdown(db, assessment_id)

@router.get("/time-series")
def get_time_series_breakdown(assessment_id: int, db: Session = Depends(get_db)):
    calcs = db.query(CarbonCalculation).filter(CarbonCalculation.assessment_id == assessment_id).all()
    # Monthly distribution
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    monthly_data = {m: {"month": m, "gross": 0.0, "reduction": 0.0, "net": 0.0} for m in months}

    for c in calcs:
        m_idx = c.month if c.month and 1 <= c.month <= 12 else None
        if m_idx:
            m_name = months[m_idx - 1]
            monthly_data[m_name]["gross"] += c.emissions_co2e
        else:
            # Distribute annual records evenly across 12 months for visualization
            for m in months:
                monthly_data[m]["gross"] += c.emissions_co2e / 12.0

    # Reductions
    reds = db.query(CarbonReductionContribution).filter(
        CarbonReductionContribution.assessment_id == assessment_id,
        CarbonReductionContribution.eligibility_status == "Eligible"
    ).all()
    total_red = sum(r.reduction_co2e for r in reds)
    for m in months:
        monthly_data[m]["reduction"] = total_red / 12.0
        monthly_data[m]["net"] = max(0.0, monthly_data[m]["gross"] - monthly_data[m]["reduction"])
        monthly_data[m]["gross"] = round(monthly_data[m]["gross"], 2)
        monthly_data[m]["reduction"] = round(monthly_data[m]["reduction"], 2)
        monthly_data[m]["net"] = round(monthly_data[m]["net"], 2)

    return list(monthly_data.values())
