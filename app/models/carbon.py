import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class EmissionFactor(Base):
    __tablename__ = "emission_factors"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(100), nullable=False) # Electricity, Stationary Fuel, Mobile Fuel, Transport, Waste, Water, Refrigerant, Process
    activity = Column(String(255), nullable=False) # e.g. Grid Electricity (India CEA v19), Diesel Combustion, Petrol Combustion, LPG, Landfill Waste, etc.
    fuel_type = Column(String(100), nullable=True)
    unit = Column(String(50), nullable=False) # kWh, Liter, kg, Tonne, kL, passenger-km, etc.
    factor = Column(Float, nullable=False) # kg CO2e per unit
    factor_unit = Column(String(50), default="kgCO2e/unit")
    scope = Column(String(50), nullable=False) # Scope 1, Scope 2, Scope 3
    source = Column(String(255), nullable=False) # CEA India 2024, IPCC 2006/2019, DEFRA 2024, US EPA 2024
    reference_year = Column(Integer, default=2024)
    region = Column(String(100), default="India") # India, Global, US, UK, EU
    valid_from = Column(String(50), nullable=True)
    valid_to = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)
    is_custom = Column(Boolean, default=False)

class CarbonCalculation(Base):
    __tablename__ = "carbon_calculations"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    campus_id = Column(Integer, ForeignKey("campuses.id"), nullable=False)
    building_id = Column(Integer, ForeignKey("buildings.id"), nullable=True)
    
    category = Column(String(100), nullable=False) # Energy, Transport, Waste, Water, Process, Refrigerant, Food
    activity = Column(String(255), nullable=False) # Description of activity
    scope = Column(String(50), nullable=False) # Scope 1, Scope 2, Scope 3
    quantity = Column(Float, nullable=False, default=0.0)
    unit = Column(String(50), nullable=False)
    emission_factor = Column(Float, nullable=False)
    emission_factor_unit = Column(String(50), default="kgCO2e/unit")
    emission_factor_source = Column(String(255), nullable=True)
    emissions_co2e = Column(Float, nullable=False, default=0.0) # tCO2e
    calculation_method = Column(String(255), default="Activity Data x Emission Factor")
    data_quality = Column(String(50), default="Bill/invoice")
    month = Column(Integer, nullable=True)
    year = Column(Integer, nullable=False, default=2025)
    calculation_date = Column(DateTime, default=datetime.datetime.utcnow)

    assessment = relationship("Assessment", back_populates="calculations")

class CarbonReductionContribution(Base):
    __tablename__ = "carbon_reduction_contributions"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    campus_id = Column(Integer, ForeignKey("campuses.id"), nullable=False)
    building_id = Column(Integer, ForeignKey("buildings.id"), nullable=True)

    category = Column(String(100), nullable=False) # Greenery, EV Transition, Solar Displaced Grid, Waste Diversion, Efficiency
    activity = Column(String(255), nullable=False)
    contribution_type = Column(String(100), nullable=False) # Carbon sequestration, Renewable-energy avoided emissions, EV transportation reduction, Energy-efficiency reduction, Waste-diversion reduction, Verified carbon removal, Other approved reduction
    
    baseline_quantity = Column(Float, default=0.0)
    baseline_unit = Column(String(50), nullable=True)
    project_quantity = Column(Float, default=0.0)
    project_unit = Column(String(50), nullable=True)
    emission_factor = Column(Float, default=0.0)
    
    gross_baseline_emissions = Column(Float, default=0.0) # tCO2e
    project_emissions = Column(Float, default=0.0) # tCO2e
    reduction_co2e = Column(Float, nullable=False, default=0.0) # tCO2e saved / removed
    
    methodology = Column(String(255), nullable=False) # Specific standard method
    source = Column(String(255), nullable=False)
    reference_year = Column(Integer, default=2025)
    eligibility_status = Column(String(50), default="Eligible") # Eligible, Not eligible, Pending review
    assumptions = Column(Text, nullable=True)
    calculation_date = Column(DateTime, default=datetime.datetime.utcnow)

    assessment = relationship("Assessment", back_populates="reduction_contributions")
