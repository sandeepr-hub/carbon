from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.scenario import Scenario
from app.schemas.schemas import ScenarioSimulationRequest, ScenarioOut
from app.engine.scenario_engine import run_whatif_simulation

router = APIRouter(prefix="/api/scenarios", tags=["What-If Scenario Simulator"])

@router.post("/simulate")
def simulate_scenario(req: ScenarioSimulationRequest, db: Session = Depends(get_db)):
    res = run_whatif_simulation(
        db,
        assessment_id=req.assessment_id,
        energy_efficiency_pct=req.energy_efficiency_pct,
        solar_capacity_addition_kw=req.solar_capacity_addition_kw,
        ev_fleet_transition_pct=req.ev_fleet_transition_pct,
        fuel_reduction_pct=req.fuel_reduction_pct,
        waste_composting_recycling_pct=req.waste_composting_recycling_pct,
        water_conservation_pct=req.water_conservation_pct,
        additional_trees_count=req.additional_trees_count
    )
    if not res:
        raise HTTPException(status_code=404, detail="Assessment or assessment summary not found")
    return res

@router.post("/save", response_model=ScenarioOut)
def save_scenario(req: ScenarioSimulationRequest, db: Session = Depends(get_db)):
    sim = run_whatif_simulation(
        db,
        assessment_id=req.assessment_id,
        energy_efficiency_pct=req.energy_efficiency_pct,
        solar_capacity_addition_kw=req.solar_capacity_addition_kw,
        ev_fleet_transition_pct=req.ev_fleet_transition_pct,
        fuel_reduction_pct=req.fuel_reduction_pct,
        waste_composting_recycling_pct=req.waste_composting_recycling_pct,
        water_conservation_pct=req.water_conservation_pct,
        additional_trees_count=req.additional_trees_count
    )
    if not sim:
        raise HTTPException(status_code=404, detail="Assessment summary not found")

    sc = Scenario(
        assessment_id=req.assessment_id,
        name=req.name or "Intervention Package",
        description=req.description,
        parameters=req.dict(),
        baseline_gross_tco2e=sim["baseline_gross_tco2e"],
        baseline_reduction_tco2e=sim["baseline_reduction_tco2e"],
        baseline_net_tco2e=sim["baseline_net_tco2e"],
        scenario_gross_tco2e=sim["scenario_gross_tco2e"],
        scenario_reduction_tco2e=sim["scenario_reduction_tco2e"],
        scenario_net_tco2e=sim["scenario_net_tco2e"],
        potential_savings_tco2e=sim["potential_savings_tco2e"],
        potential_reduction_pct=sim["potential_reduction_pct"]
    )
    db.add(sc)
    db.commit()
    db.refresh(sc)
    return sc

@router.get("/list", response_model=list[ScenarioOut])
def list_saved_scenarios(assessment_id: int, db: Session = Depends(get_db)):
    return db.query(Scenario).filter(Scenario.assessment_id == assessment_id).all()
