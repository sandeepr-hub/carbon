import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.organization import Organization, User
from app.models.campus import Campus, Building, Occupancy
from app.models.assessment import Assessment, AssessmentSummary
from app.models.activity import (
    EnergyRecord, RenewableRecord, TransportRecord, WasteRecord,
    WaterRecord, WastewaterRecord, GreenRecord, FoodRecord
)
from app.models.carbon import EmissionFactor, CarbonCalculation, CarbonReductionContribution
from app.seed.factors_seed import seed_emission_factors
from app.seed.demo_data import seed_demo_data
from app.engine.carbon_calculator import calculate_gross_emissions
from app.engine.reduction_calculator import calculate_reduction_contributions
from app.engine.anti_double_counting import check_solar_double_counting, validate_activity_quantity
from app.engine.aggregator import aggregate_assessment_summary, get_building_wise_results
from app.engine.scenario_engine import run_whatif_simulation
from app.engine.report_generator import generate_pdf_report, generate_excel_report, generate_csv_report

@pytest.fixture(scope="module")
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    seed_emission_factors(session)
    seed_demo_data(session)
    yield session
    session.close()

def test_emission_factors_seeded(db_session):
    factors = db_session.query(EmissionFactor).all()
    assert len(factors) >= 15
    grid_ef = db_session.query(EmissionFactor).filter(EmissionFactor.activity.ilike("%Grid Electricity%")).first()
    assert grid_ef is not None
    assert grid_ef.factor == 0.716 # India CEA v19 factor

def test_gross_carbon_calculation(db_session):
    # Assessment ID 1 is Christ University Kengeri Campus 2025
    calcs = calculate_gross_emissions(db_session, 1)
    assert len(calcs) > 0
    
    # Check Scope 1, 2, 3
    scope1_emissions = sum(c.emissions_co2e for c in calcs if c.scope == "Scope 1")
    scope2_emissions = sum(c.emissions_co2e for c in calcs if c.scope == "Scope 2")
    scope3_emissions = sum(c.emissions_co2e for c in calcs if c.scope == "Scope 3")

    assert scope1_emissions > 100.0 # DG diesel, fleet diesel, LPG
    assert scope2_emissions > 1200.0 # ~1.85M kWh * 0.716 / 1000 ~ 1324 tCO2e
    assert scope3_emissions > 50.0 # Commuting, waste, water, STP

def test_reduction_contributions_and_safeguards(db_session):
    reds = calculate_reduction_contributions(db_session, 1)
    assert len(reds) > 0

    # 1. Sequestration from 2,800 trees
    tree_seq = [r for r in reds if r.contribution_type == "Carbon sequestration"]
    assert len(tree_seq) > 0
    assert tree_seq[0].reduction_co2e == 61.6 # 2800 * 22 / 1000

    # 2. Anti-double-counting check on solar
    is_safe, msg = check_solar_double_counting(is_onsite_consumed=True)
    assert is_safe is False
    assert "replaces grid electricity imports" in msg

    # 3. Non-negative validation
    with pytest.raises(ValueError):
        validate_activity_quantity("Diesel", -500.0)

def test_summary_aggregation(db_session):
    summary = aggregate_assessment_summary(db_session, 1)
    assert summary is not None
    assert summary.gross_emissions > 1000.0
    assert summary.eligible_reductions > 50.0
    assert summary.net_footprint == round(summary.gross_emissions - summary.eligible_reductions, 4)
    assert summary.gross_per_person > 0
    assert summary.renewable_percentage > 20.0 # 720k solar on 2.57M total ~ 28%

def test_building_wise_results(db_session):
    buildings = get_building_wise_results(db_session, 1)
    assert len(buildings) == 13 # 13 buildings of Christ University Kengeri Campus
    # First building should have highest gross emissions
    assert buildings[0]["gross_tco2e"] >= buildings[-1]["gross_tco2e"]

def test_whatif_simulator(db_session):
    sim = run_whatif_simulation(
        db_session,
        assessment_id=1,
        energy_efficiency_pct=20.0,
        solar_capacity_addition_kw=250.0,
        ev_fleet_transition_pct=50.0,
        additional_trees_count=1000
    )
    assert sim is not None
    assert sim["potential_savings_tco2e"] > 200.0
    assert sim["potential_reduction_pct"] > 10.0
    assert sim["scenario_net_tco2e"] < sim["baseline_net_tco2e"]

def test_reports_generation(db_session):
    pdf_path = generate_pdf_report(db_session, 1)
    assert pdf_path.endswith(".pdf")

    excel_path = generate_excel_report(db_session, 1)
    assert excel_path.endswith(".xlsx")

    csv_path = generate_csv_report(db_session, 1)
    assert csv_path.endswith(".csv")
