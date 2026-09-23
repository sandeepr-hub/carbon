import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class EnergyRecord(Base):
    __tablename__ = "energy_records"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    campus_id = Column(Integer, ForeignKey("campuses.id"), nullable=False)
    building_id = Column(Integer, ForeignKey("buildings.id"), nullable=True) # None = Whole Campus
    data_scope = Column(String(50), default="Whole Campus") # Whole Campus, Building, Canteen, Fleet
    energy_type = Column(String(100), nullable=False) # Grid Electricity, Diesel Generator Electricity, Natural Gas, LPG, Petrol, Diesel, Biomass, Other
    source = Column(String(100), default="State Grid") # e.g. Grid / DG / Utility / Solar
    quantity = Column(Float, nullable=False, default=0.0)
    unit = Column(String(50), nullable=False, default="kWh") # kWh, MWh, Liters, kg, m3
    purpose = Column(String(100), default="Campus Operations") # DG Generator, College Bus, Campus Vehicle, Kitchen, Other
    data_period = Column(String(50), default="Annual") # Annual, Monthly
    month = Column(Integer, nullable=True) # 1-12 or None for annual
    year = Column(Integer, nullable=False, default=2025)
    data_source = Column(String(255), default="Utility Electricity Bill")
    data_quality = Column(String(50), default="Bill/invoice") # Measured, Meter reading, Bill/invoice, Estimated
    notes = Column(Text, nullable=True)

class RenewableRecord(Base):
    __tablename__ = "renewable_records"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    campus_id = Column(Integer, ForeignKey("campuses.id"), nullable=False)
    building_id = Column(Integer, ForeignKey("buildings.id"), nullable=True)
    technology = Column(String(100), default="Solar PV") # Rooftop Solar PV, Ground-Mounted Solar, Wind, Biogas
    capacity_kw = Column(Float, default=0.0) # Installed capacity in kW / kWp
    generation_kwh = Column(Float, nullable=False, default=0.0) # Annual Solar Generation (kWh)
    displaced_grid_kwh = Column(Float, default=0.0)
    is_onsite_consumed = Column(Boolean, default=True) # Onsite vs Exported
    installation_location = Column(String(255), default="Campus Rooftops & Open Grounds")
    data_quality = Column(String(50), default="Generation Meter")
    month = Column(Integer, nullable=True)
    year = Column(Integer, nullable=False, default=2025)
    notes = Column(Text, nullable=True)

class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    campus_id = Column(Integer, ForeignKey("campuses.id"), nullable=False)
    name = Column(String(255), nullable=False)
    vehicle_type = Column(String(100), nullable=False) # Bus, Car, Van, Tractor, Tempo, Ambulance, Two Wheeler, Electric Vehicle, Other
    fuel_type = Column(String(50), nullable=False) # Diesel, Petrol, CNG, Electricity, Hybrid, Biofuel
    ownership = Column(String(50), default="Campus-owned") # Campus-owned, Contracted, Staff-owned
    registration = Column(String(50), nullable=True)
    capacity = Column(Integer, default=4)
    active = Column(Boolean, default=True)

    campus = relationship("Campus", back_populates="vehicles")

class TransportRecord(Base):
    __tablename__ = "transport_records"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    campus_id = Column(Integer, ForeignKey("campuses.id"), nullable=False)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=True)
    building_id = Column(Integer, ForeignKey("buildings.id"), nullable=True)
    data_scope = Column(String(50), default="Whole Campus")
    record_type = Column(String(50), default="Fleet") # Fleet, Commuting, EV Charging
    mode = Column(String(100), nullable=True) # Bus, Car, Van, Tractor, Tempo, Ambulance, Two Wheeler, Electric Vehicle, Other
    fuel_type = Column(String(50), nullable=True) # Diesel, Petrol, CNG, Electricity
    vehicle_count = Column(Integer, default=1)
    distance_km = Column(Float, default=0.0)
    fuel_quantity = Column(Float, default=0.0)
    fuel_unit = Column(String(50), default="Liters") # Liters, kg, kWh
    passengers = Column(Integer, default=1)
    frequency = Column(String(50), default="Annual") # Annual, Daily, Monthly
    charging_electricity_kwh = Column(Float, default=0.0)
    is_ev_in_grid_electricity = Column(Boolean, default=True) # Safeguard against double counting
    charging_location = Column(String(100), default="Campus EV Charging Station")
    month = Column(Integer, nullable=True)
    year = Column(Integer, nullable=False, default=2025)
    data_quality = Column(String(50), default="Logbook / Fuel Invoices")
    notes = Column(Text, nullable=True)

class WasteRecord(Base):
    __tablename__ = "waste_records"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    campus_id = Column(Integer, ForeignKey("campuses.id"), nullable=False)
    building_id = Column(Integer, ForeignKey("buildings.id"), nullable=True)
    data_scope = Column(String(50), default="Whole Campus")
    waste_type = Column(String(100), nullable=False) # Food Waste, Paper, Plastic, Metal, Glass, Mixed Waste, E-waste, Biomedical, Other
    quantity = Column(Float, nullable=False, default=0.0)
    unit = Column(String(50), default="kg") # kg, Tonnes
    disposal_method = Column(String(100), nullable=False) # Recycling, Composting, Landfill, Incineration, Reuse, Other
    data_period = Column(String(50), default="Annual")
    month = Column(Integer, nullable=True)
    year = Column(Integer, nullable=False, default=2025)
    data_quality = Column(String(50), default="Measured")
    notes = Column(Text, nullable=True)

class WaterRecord(Base):
    __tablename__ = "water_records"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    campus_id = Column(Integer, ForeignKey("campuses.id"), nullable=False)
    building_id = Column(Integer, ForeignKey("buildings.id"), nullable=True)
    data_scope = Column(String(50), default="Whole Campus")
    source = Column(String(100), nullable=False) # Municipal Water, Borewell, Tanker, Rainwater, Other
    usage_type = Column(String(100), default="Campus Domestic & Facilities")
    quantity = Column(Float, nullable=False, default=0.0)
    unit = Column(String(50), default="kL") # kL (Kiloliters / m3), Liters
    data_period = Column(String(50), default="Annual")
    month = Column(Integer, nullable=True)
    year = Column(Integer, nullable=False, default=2025)
    data_quality = Column(String(50), default="Flow Meter Reading")
    notes = Column(Text, nullable=True)

class WastewaterRecord(Base):
    __tablename__ = "wastewater_records"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    campus_id = Column(Integer, ForeignKey("campuses.id"), nullable=False)
    building_id = Column(Integer, ForeignKey("buildings.id"), nullable=True)
    facility_name = Column(String(255), default="Central Sewage Treatment Plant (STP)")
    treatment_type = Column(String(100), default="SBR STP") # SBR STP, MBBR STP, Activated Sludge, Phytoremediation, Septic
    capacity_kld = Column(Float, default=0.0)
    wastewater_quantity = Column(Float, default=0.0)
    treated_quantity = Column(Float, default=0.0)
    reused_quantity = Column(Float, default=0.0) # Landscape irrigation & flushing
    electricity_kwh = Column(Float, default=0.0)
    sludge_kg = Column(Float, default=0.0)
    data_period = Column(String(50), default="Annual")
    month = Column(Integer, nullable=True)
    year = Column(Integer, nullable=False, default=2025)
    data_quality = Column(String(50), default="Measured")
    notes = Column(Text, nullable=True)

class GreenRecord(Base):
    __tablename__ = "green_records"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    campus_id = Column(Integer, ForeignKey("campuses.id"), nullable=False)
    building_id = Column(Integer, ForeignKey("buildings.id"), nullable=True)
    green_area_sqm = Column(Float, default=0.0)
    tree_count = Column(Integer, default=0)
    plant_count = Column(Integer, default=0)
    tree_species = Column(Text, nullable=True) # Neem, Teak, Peepal, Mango, Native evergreen
    annual_sequestration_tco2e = Column(Float, default=0.0)
    maintenance_electricity_kwh = Column(Float, default=0.0)
    irrigation_water_kl = Column(Float, default=0.0)
    methodology = Column(String(255), default="FSI Tree Biomass & IPCC Good Practice Guidance (22.0 kg CO2/tree/year)")
    data_quality = Column(String(50), default="Physical Tree Census")
    year = Column(Integer, nullable=False, default=2025)
    notes = Column(Text, nullable=True)

class WaterConservationRecord(Base):
    __tablename__ = "water_conservation_records"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    campus_id = Column(Integer, ForeignKey("campuses.id"), nullable=False)
    water_saved_kl = Column(Float, nullable=False, default=0.0)
    unit = Column(String(50), default="kL")
    method = Column(String(100), default="Rainwater harvesting") # Rainwater harvesting, Low-flow fixtures, Reuse of treated wastewater, Water recycling, Other
    annual_saving_tco2e = Column(Float, default=0.0)
    data_quality = Column(String(50), default="Measured / Flow Meters")
    year = Column(Integer, nullable=False, default=2025)
    notes = Column(Text, nullable=True)

class WaterBodyRecord(Base):
    __tablename__ = "water_body_records"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    campus_id = Column(Integer, ForeignKey("campuses.id"), nullable=False)
    body_count = Column(Integer, default=1)
    total_area_sqm = Column(Float, default=0.0)
    body_type = Column(String(100), default="Lake") # Pond, Lake, Artificial Pond, Wetland, Other
    carbon_benefit_tco2e = Column(Float, default=0.0)
    methodology = Column(String(255), default="Wetland Biological Ecosystem Conservation Factor")
    data_quality = Column(String(50), default="GIS Mapping / Ground Survey")
    year = Column(Integer, nullable=False, default=2025)
    notes = Column(Text, nullable=True)

class AnimalRecord(Base):
    __tablename__ = "animal_records"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    campus_id = Column(Integer, ForeignKey("campuses.id"), nullable=False)
    animal_type = Column(String(100), nullable=False) # Cattle / Dairy, Poultry, Goats / Sheep, Horses, Deer / Wildlife, Other
    animal_count = Column(Integer, default=0)
    management_method = Column(String(100), default="On-site Manure Composting & Biogas")
    carbon_benefit_tco2e = Column(Float, default=0.0) # Informational unless verified methodology exists
    methodology = Column(String(255), default="Informational Census / Controlled Anaerobic Manure Management")
    data_quality = Column(String(50), default="Census")
    year = Column(Integer, nullable=False, default=2025)
    notes = Column(Text, nullable=True)

class FoodRecord(Base):
    __tablename__ = "food_records"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    campus_id = Column(Integer, ForeignKey("campuses.id"), nullable=False)
    building_id = Column(Integer, ForeignKey("buildings.id"), nullable=True) # Optional building association
    canteen_name = Column(String(255), default="Main Dining Hall & Canteen")
    operating_days = Column(Integer, default=280)
    meals_served = Column(Integer, default=0)
    lpg_kg = Column(Float, default=0.0)
    electricity_kwh = Column(Float, default=0.0)
    food_waste_kg = Column(Float, default=0.0)
    water_kl = Column(Float, default=0.0)
    month = Column(Integer, nullable=True)
    year = Column(Integer, nullable=False, default=2025)
    notes = Column(Text, nullable=True)

class IndustrialRecord(Base):
    __tablename__ = "industrial_records"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    campus_id = Column(Integer, ForeignKey("campuses.id"), nullable=False)
    building_id = Column(Integer, ForeignKey("buildings.id"), nullable=True)
    production_name = Column(String(255), default="Finished Goods Output")
    production_quantity = Column(Float, default=0.0)
    production_unit = Column(String(50), default="Tonnes")
    process_type = Column(String(100), nullable=True)
    process_emissions_tco2e = Column(Float, default=0.0)
    refrigerant_type = Column(String(50), default="R-410A")
    refrigerant_leakage_kg = Column(Float, default=0.0)
    month = Column(Integer, nullable=True)
    year = Column(Integer, nullable=False, default=2025)
    notes = Column(Text, nullable=True)
