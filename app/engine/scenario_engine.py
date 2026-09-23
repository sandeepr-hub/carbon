from sqlalchemy.orm import Session
from app.models.assessment import Assessment, AssessmentSummary
from app.models.activity import EnergyRecord, TransportRecord, WasteRecord, WaterRecord, GreenRecord
from app.models.scenario import Scenario

def run_whatif_simulation(
    db: Session,
    assessment_id: int,
    energy_efficiency_pct: float = 0.0,
    solar_capacity_addition_kw: float = 0.0,
    ev_fleet_transition_pct: float = 0.0,
    fuel_reduction_pct: float = 0.0,
    waste_composting_recycling_pct: float = 0.0,
    water_conservation_pct: float = 0.0,
    additional_trees_count: int = 0
):
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment or not assessment.summary:
        return None

    base_summary = assessment.summary
    base_gross = base_summary.gross_emissions
    base_reductions = base_summary.eligible_reductions
    base_net = base_summary.net_footprint

    # 1. Energy Efficiency Savings on Scope 2
    scope2_base = base_summary.scope2
    elec_savings_tco2e = (scope2_base * (energy_efficiency_pct / 100.0))

    # 2. Solar Capacity Addition (assuming 1440 kWh/kWp annual generation for solar PV in India)
    solar_gen_kwh = solar_capacity_addition_kw * 1440.0
    solar_savings_tco2e = (solar_gen_kwh * 0.716) / 1000.0

    # 3. Fuel Reduction on Scope 1 stationary combustion
    scope1_base = base_summary.scope1
    fuel_savings_tco2e = (scope1_base * 0.4 * (fuel_reduction_pct / 100.0)) # stationary portion

    # 4. EV Fleet Transition (assuming ~50% of scope 1 is fleet)
    fleet_portion = scope1_base * 0.6
    ev_savings_tco2e = (fleet_portion * (ev_fleet_transition_pct / 100.0) * 0.7) # 70% net savings after EV electricity

    # 5. Waste Composting & Recycling Increase
    scope3_base = base_summary.scope3
    waste_savings_tco2e = (scope3_base * 0.15 * (waste_composting_recycling_pct / 100.0))

    # 6. Water Conservation
    water_savings_tco2e = (scope3_base * 0.1 * (water_conservation_pct / 100.0))

    # 7. Additional Tree Sequestration
    additional_seq_tco2e = (additional_trees_count * 22.0) / 1000.0

    total_gross_reduction = elec_savings_tco2e + solar_savings_tco2e + fuel_savings_tco2e + ev_savings_tco2e + waste_savings_tco2e + water_savings_tco2e
    scenario_gross = max(0.0, base_gross - total_gross_reduction)
    scenario_reductions = base_reductions + additional_seq_tco2e
    scenario_net = max(0.0, scenario_gross - scenario_reductions)

    potential_savings = max(0.0, base_net - scenario_net)
    potential_pct = (potential_savings / base_net * 100.0) if base_net > 0 else 0.0

    return {
        "assessment_id": assessment_id,
        "baseline_gross_tco2e": round(base_gross, 4),
        "baseline_reduction_tco2e": round(base_reductions, 4),
        "baseline_net_tco2e": round(base_net, 4),
        "scenario_gross_tco2e": round(scenario_gross, 4),
        "scenario_reduction_tco2e": round(scenario_reductions, 4),
        "scenario_net_tco2e": round(scenario_net, 4),
        "potential_savings_tco2e": round(potential_savings, 4),
        "potential_reduction_pct": round(potential_pct, 2),
        "breakdown_savings": {
            "energy_efficiency_tco2e": round(elec_savings_tco2e, 4),
            "solar_addition_tco2e": round(solar_savings_tco2e, 4),
            "ev_transition_tco2e": round(ev_savings_tco2e, 4),
            "fuel_reduction_tco2e": round(fuel_savings_tco2e, 4),
            "waste_diversion_tco2e": round(waste_savings_tco2e, 4),
            "water_conservation_tco2e": round(water_savings_tco2e, 4),
            "additional_sequestration_tco2e": round(additional_seq_tco2e, 4)
        }
    }
