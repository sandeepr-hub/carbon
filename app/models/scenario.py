import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class Scenario(Base):
    __tablename__ = "scenarios"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    parameters = Column(JSON, default=dict) # e.g. {"solar_increase_pct": 50, "ev_fleet_pct": 60, ...}
    
    baseline_gross_tco2e = Column(Float, default=0.0)
    baseline_reduction_tco2e = Column(Float, default=0.0)
    baseline_net_tco2e = Column(Float, default=0.0)

    scenario_gross_tco2e = Column(Float, default=0.0)
    scenario_reduction_tco2e = Column(Float, default=0.0)
    scenario_net_tco2e = Column(Float, default=0.0)

    potential_savings_tco2e = Column(Float, default=0.0)
    potential_reduction_pct = Column(Float, default=0.0)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    assessment = relationship("Assessment", back_populates="scenarios")
    changes = relationship("ScenarioChange", back_populates="scenario", cascade="all, delete-orphan")

class ScenarioChange(Base):
    __tablename__ = "scenario_changes"

    id = Column(Integer, primary_key=True, index=True)
    scenario_id = Column(Integer, ForeignKey("scenarios.id"), nullable=False)
    category = Column(String(100), nullable=False) # Electricity, Solar, Fleet, Waste, Water, Greenery
    parameter = Column(String(100), nullable=False)
    change_type = Column(String(50), default="Percentage") # Percentage, Absolute
    change_value = Column(Float, default=0.0)

    scenario = relationship("Scenario", back_populates="changes")

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    campus_type = Column(String(100), default="All") # All, University, School, Hospital, Industrial, etc.
    category = Column(String(100), nullable=False) # Electricity, Fuel, Transport, Waste, Water, Cooling, Greenery
    condition_metric = Column(String(255), nullable=True) # e.g. scope2_pct > 50, transport_share > 30
    title = Column(String(255), nullable=False)
    recommendation_text = Column(Text, nullable=False)
    intervention_type = Column(String(100), default="Emission Reduction") # Emission Reduction, Carbon Sequestration / Removal, Energy Efficiency
    priority = Column(String(50), default="High") # High, Medium, Low
    estimated_reduction_pct = Column(Float, default=15.0)
    action_type = Column(String(100), default="Technology Upgrade")
