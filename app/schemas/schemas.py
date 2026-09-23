from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
import datetime

# --- Auth & Users ---
class UserLogin(BaseModel):
    email: str
    password: str

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: str = "ADMIN"
    organization_id: Optional[int] = None

class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: str
    active: bool
    organization_id: Optional[int] = None
    created_at: Optional[datetime.datetime] = None
    class Config:
        from_attributes = True

# --- Organization ---
class OrganizationCreate(BaseModel):
    name: str
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None

class OrganizationOut(BaseModel):
    id: int
    name: str
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    class Config:
        from_attributes = True

# --- Campus & Buildings ---
class BuildingCreate(BaseModel):
    building_code: Optional[str] = None
    name: str
    building_type: str = "Academic"
    floors: int = 1
    built_up_area: float = 0.0
    area_unit: str = "Sq Meters"
    students_on_campus: int = 0
    students_off_campus: int = 0
    faculty_count: int = 0
    non_teaching_count: int = 0
    other_occupants: int = 0
    occupancy: int = 0
    operating_hours: float = 8.0
    year_constructed: Optional[int] = None
    description: Optional[str] = None

class BuildingOut(BuildingCreate):
    id: int
    campus_id: int
    built_up_area_sqm: float = 0.0
    class Config:
        from_attributes = True

class BuildingPopulationUpdate(BaseModel):
    building_id: int
    students_on_campus: int = 0
    students_off_campus: int = 0
    faculty_count: int = 0
    non_teaching_count: int = 0
    other_occupants: int = 0

class CampusCreate(BaseModel):
    organization_id: Optional[int] = 1
    name: str
    campus_type: str = "University / College"
    country: str = "India"
    state: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    
    # Area
    area: float = 0.0
    area_unit: str = "Acres" # Acres or m²
    built_up_percentage: float = 50.0 # Built-up %
    
    # Operating parameters
    operating_days_per_year: int = 280
    operating_hours_per_day: float = 8.0
    assessment_year: int = 2025

    # Population Breakdown
    students_on_campus: int = 0
    students_off_campus: int = 0
    faculty_count: int = 0
    non_teaching_count: int = 0

    # Buildings
    num_buildings: int = 1
    buildings: Optional[List[BuildingCreate]] = None

    # Negative activities checklist
    negative_activities: Optional[Dict[str, bool]] = None
    config: Optional[Dict[str, Any]] = None

class CampusOut(BaseModel):
    id: int
    organization_id: int
    name: str
    campus_type: str
    country: str
    state: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    
    area: float
    area_unit: str
    area_sqm: float
    built_up_percentage: float
    calculated_built_up_area_acres: float
    calculated_built_up_area_sqm: float
    total_built_up_area_sqm: float

    operating_days_per_year: int
    operating_hours_per_day: float
    assessment_year: int

    students_on_campus: int
    students_off_campus: int
    faculty_count: int
    non_teaching_count: int
    total_student_population: int
    total_staff_population: int
    population: int

    num_buildings: int
    negative_activities: Optional[Dict[str, Any]] = None
    config: Optional[Dict[str, Any]] = None
    buildings: List[BuildingOut] = []
    created_at: Optional[datetime.datetime] = None
    class Config:
        from_attributes = True

# --- Assessment ---
class AssessmentCreate(BaseModel):
    campus_id: int
    name: str
    reporting_year: int = 2025
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    methodology: str = "GHG Protocol Corporate Standard / ISO 14064-1"
    boundary_description: Optional[str] = None

class AssessmentSummaryOut(BaseModel):
    id: int
    assessment_id: int
    scope1: float
    scope2: float
    scope3: float
    gross_emissions: float
    eligible_reductions: float
    net_footprint: float
    sequestration: float
    population: int
    gross_per_person: float
    reduction_per_person: float
    net_per_person: float
    built_up_area_sqm: float
    gross_per_area: float
    reduction_per_area: float
    net_per_area: float
    renewable_percentage: float
    grid_electricity_displaced_kwh: float
    total_energy_consumption_kwh: float
    total_water_consumption_kl: float
    total_waste_generated_kg: float
    waste_diversion_rate: float
    updated_at: Optional[datetime.datetime] = None
    class Config:
        from_attributes = True

class AssessmentOut(BaseModel):
    id: int
    campus_id: int
    name: str
    reporting_year: int
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    status: str
    methodology: str
    boundary_description: Optional[str] = None
    created_by: str
    created_at: Optional[datetime.datetime] = None
    summary: Optional[AssessmentSummaryOut] = None
    class Config:
        from_attributes = True

# --- Activity Data Schemas ---
class EnergyRecordCreate(BaseModel):
    building_id: Optional[int] = None
    data_scope: str = "Whole Campus"
    energy_type: str
    source: str = "State Grid"
    quantity: float
    unit: str = "kWh"
    purpose: str = "Campus Operations"
    data_period: str = "Annual"
    month: Optional[int] = None
    year: int = 2025
    data_source: str = "Utility Bill"
    data_quality: str = "Bill/invoice"
    notes: Optional[str] = None

class EnergyRecordOut(EnergyRecordCreate):
    id: int
    assessment_id: int
    campus_id: int
    class Config:
        from_attributes = True

class RenewableRecordCreate(BaseModel):
    building_id: Optional[int] = None
    technology: str = "Solar PV"
    capacity_kw: float = 0.0
    generation_kwh: float
    displaced_grid_kwh: Optional[float] = 0.0
    is_onsite_consumed: bool = True
    installation_location: str = "Campus Rooftop"
    data_quality: str = "Generation Meter"
    month: Optional[int] = None
    year: int = 2025
    notes: Optional[str] = None

class RenewableRecordOut(RenewableRecordCreate):
    id: int
    assessment_id: int
    campus_id: int
    class Config:
        from_attributes = True

class VehicleCreate(BaseModel):
    name: str
    vehicle_type: str = "Bus"
    fuel_type: str = "Diesel"
    ownership: str = "Campus-owned"
    registration: Optional[str] = None
    capacity: int = 40
    active: bool = True

class VehicleOut(VehicleCreate):
    id: int
    campus_id: int
    class Config:
        from_attributes = True

class TransportRecordCreate(BaseModel):
    vehicle_id: Optional[int] = None
    building_id: Optional[int] = None
    data_scope: str = "Whole Campus"
    record_type: str = "Fleet" # Fleet, Commuting, EV Charging
    mode: Optional[str] = "Campus Bus"
    fuel_type: Optional[str] = "Diesel"
    vehicle_count: int = 1
    distance_km: float = 0.0
    fuel_quantity: float = 0.0
    fuel_unit: str = "Liters"
    passengers: int = 1
    frequency: str = "Annual"
    charging_electricity_kwh: float = 0.0
    is_ev_in_grid_electricity: bool = True
    charging_location: Optional[str] = "Campus EV Station"
    month: Optional[int] = None
    year: int = 2025
    data_quality: str = "Fuel Invoice / Log"
    notes: Optional[str] = None

class TransportRecordOut(TransportRecordCreate):
    id: int
    assessment_id: int
    campus_id: int
    class Config:
        from_attributes = True

class WasteRecordCreate(BaseModel):
    building_id: Optional[int] = None
    data_scope: str = "Whole Campus"
    waste_type: str # Food Waste, Paper, Plastic, Metal, Glass, Mixed Waste, E-waste, Biomedical, Other
    quantity: float
    unit: str = "kg"
    disposal_method: str = "Composting" # Recycling, Composting, Landfill, Incineration, Reuse
    data_period: str = "Annual"
    month: Optional[int] = None
    year: int = 2025
    data_quality: str = "Measured"
    notes: Optional[str] = None

class WasteRecordOut(WasteRecordCreate):
    id: int
    assessment_id: int
    campus_id: int
    class Config:
        from_attributes = True

class WaterRecordCreate(BaseModel):
    building_id: Optional[int] = None
    data_scope: str = "Whole Campus"
    source: str = "Municipal Water" # Municipal Water, Borewell, Tanker, Rainwater, Other
    usage_type: str = "Campus Domestic"
    quantity: float
    unit: str = "kL"
    data_period: str = "Annual"
    month: Optional[int] = None
    year: int = 2025
    data_quality: str = "Flow Meter Reading"
    notes: Optional[str] = None

class WaterRecordOut(WaterRecordCreate):
    id: int
    assessment_id: int
    campus_id: int
    class Config:
        from_attributes = True

class WastewaterRecordCreate(BaseModel):
    building_id: Optional[int] = None
    facility_name: str = "Central STP"
    treatment_type: str = "SBR STP"
    capacity_kld: float = 0.0
    wastewater_quantity: float = 0.0
    treated_quantity: float = 0.0
    reused_quantity: float = 0.0
    electricity_kwh: float = 0.0
    sludge_kg: float = 0.0
    data_period: str = "Annual"
    month: Optional[int] = None
    year: int = 2025
    data_quality: str = "Measured"
    notes: Optional[str] = None

class WastewaterRecordOut(WastewaterRecordCreate):
    id: int
    assessment_id: int
    campus_id: int
    class Config:
        from_attributes = True

class GreenRecordCreate(BaseModel):
    building_id: Optional[int] = None
    green_area_sqm: float = 0.0
    tree_count: int = 0
    plant_count: int = 0
    tree_species: Optional[str] = None
    annual_sequestration_tco2e: Optional[float] = 0.0
    maintenance_electricity_kwh: float = 0.0
    irrigation_water_kl: float = 0.0
    methodology: str = "FSI Tree Biomass & IPCC Good Practice Guidance (22.0 kg CO2/tree/year)"
    data_quality: str = "Physical Tree Census"
    year: int = 2025
    notes: Optional[str] = None

class GreenRecordOut(GreenRecordCreate):
    id: int
    assessment_id: int
    campus_id: int
    class Config:
        from_attributes = True

class WaterConservationRecordCreate(BaseModel):
    water_saved_kl: float
    unit: str = "kL"
    method: str = "Rainwater harvesting"
    annual_saving_tco2e: float = 0.0
    data_quality: str = "Measured"
    year: int = 2025
    notes: Optional[str] = None

class WaterConservationRecordOut(WaterConservationRecordCreate):
    id: int
    assessment_id: int
    campus_id: int
    class Config:
        from_attributes = True

class WaterBodyRecordCreate(BaseModel):
    body_count: int = 1
    total_area_sqm: float = 0.0
    body_type: str = "Lake"
    carbon_benefit_tco2e: float = 0.0
    methodology: str = "Wetland Biological Ecosystem Conservation Factor"
    data_quality: str = "GIS Survey"
    year: int = 2025
    notes: Optional[str] = None

class WaterBodyRecordOut(WaterBodyRecordCreate):
    id: int
    assessment_id: int
    campus_id: int
    class Config:
        from_attributes = True

class AnimalRecordCreate(BaseModel):
    animal_type: str
    animal_count: int = 0
    management_method: str = "On-site Manure Composting & Biogas"
    carbon_benefit_tco2e: float = 0.0
    methodology: str = "Informational Census / Anaerobic Manure Management"
    data_quality: str = "Census"
    year: int = 2025
    notes: Optional[str] = None

class AnimalRecordOut(AnimalRecordCreate):
    id: int
    assessment_id: int
    campus_id: int
    class Config:
        from_attributes = True

class FoodRecordCreate(BaseModel):
    building_id: Optional[int] = None
    canteen_name: str = "Main Dining Hall & Canteen"
    operating_days: int = 280
    meals_served: int = 0
    lpg_kg: float = 0.0
    electricity_kwh: float = 0.0
    food_waste_kg: float = 0.0
    water_kl: float = 0.0
    month: Optional[int] = None
    year: int = 2025
    notes: Optional[str] = None

class FoodRecordOut(FoodRecordCreate):
    id: int
    assessment_id: int
    campus_id: int
    class Config:
        from_attributes = True

class IndustrialRecordCreate(BaseModel):
    building_id: Optional[int] = None
    production_name: str = "Finished Goods Output"
    production_quantity: float = 0.0
    production_unit: str = "Tonnes"
    process_type: Optional[str] = None
    process_emissions_tco2e: float = 0.0
    refrigerant_type: str = "R-410A"
    refrigerant_leakage_kg: float = 0.0
    month: Optional[int] = None
    year: int = 2025
    notes: Optional[str] = None

class IndustrialRecordOut(IndustrialRecordCreate):
    id: int
    assessment_id: int
    campus_id: int
    class Config:
        from_attributes = True

# --- Emission Factors ---
class EmissionFactorCreate(BaseModel):
    category: str
    activity: str
    fuel_type: Optional[str] = None
    unit: str
    factor: float
    factor_unit: str = "kgCO2e/unit"
    scope: str
    source: str
    reference_year: int = 2024
    region: str = "India"
    valid_from: Optional[str] = None
    valid_to: Optional[str] = None
    notes: Optional[str] = None
    is_custom: bool = True

class EmissionFactorOut(EmissionFactorCreate):
    id: int
    class Config:
        from_attributes = True

# --- Calculation & Reduction Schemas ---
class CarbonCalculationOut(BaseModel):
    id: int
    assessment_id: int
    campus_id: int
    building_id: Optional[int] = None
    category: str
    activity: str
    scope: str
    quantity: float
    unit: str
    emission_factor: float
    emission_factor_unit: str
    emission_factor_source: Optional[str] = None
    emissions_co2e: float
    calculation_method: str
    data_quality: str
    month: Optional[int] = None
    year: int
    calculation_date: Optional[datetime.datetime] = None
    class Config:
        from_attributes = True

class CarbonReductionContributionOut(BaseModel):
    id: int
    assessment_id: int
    campus_id: int
    building_id: Optional[int] = None
    category: str
    activity: str
    contribution_type: str
    baseline_quantity: float
    baseline_unit: Optional[str] = None
    project_quantity: float
    project_unit: Optional[str] = None
    emission_factor: float
    gross_baseline_emissions: float
    project_emissions: float
    reduction_co2e: float
    methodology: str
    source: str
    reference_year: int
    eligibility_status: str
    assumptions: Optional[str] = None
    calculation_date: Optional[datetime.datetime] = None
    class Config:
        from_attributes = True

# --- Scenario Simulation ---
class ScenarioSimulationRequest(BaseModel):
    assessment_id: int
    name: Optional[str] = "Simulation Run"
    description: Optional[str] = None
    energy_efficiency_pct: float = 0.0
    solar_capacity_addition_kw: float = 0.0
    ev_fleet_transition_pct: float = 0.0
    fuel_reduction_pct: float = 0.0
    waste_composting_recycling_pct: float = 0.0
    water_conservation_pct: float = 0.0
    additional_trees_count: int = 0

class ScenarioOut(BaseModel):
    id: Optional[int] = None
    assessment_id: int
    name: str
    description: Optional[str] = None
    parameters: Dict[str, Any] = {}
    baseline_gross_tco2e: float
    baseline_reduction_tco2e: float
    baseline_net_tco2e: float
    scenario_gross_tco2e: float
    scenario_reduction_tco2e: float
    scenario_net_tco2e: float
    potential_savings_tco2e: float
    potential_reduction_pct: float
    created_at: Optional[datetime.datetime] = None
    class Config:
        from_attributes = True

# --- Recommendation ---
class RecommendationOut(BaseModel):
    id: int
    campus_type: str
    category: str
    title: str
    recommendation_text: str
    intervention_type: str
    priority: str
    estimated_reduction_pct: float
    action_type: str
    class Config:
        from_attributes = True
