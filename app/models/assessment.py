import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True)
    campus_id = Column(Integer, ForeignKey("campuses.id"), nullable=False)
    name = Column(String(255), nullable=False)
    reporting_year = Column(Integer, nullable=False, default=2025)
    start_date = Column(String(50), nullable=True)
    end_date = Column(String(50), nullable=True)
    status = Column(String(50), default="Draft") # Draft, In Progress, Under Review, Completed, Locked
    methodology = Column(String(255), default="GHG Protocol Corporate Standard / ISO 14064-1")
    boundary_description = Column(Text, nullable=True)
    created_by = Column(String(255), default="System Admin")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    campus = relationship("Campus", back_populates="assessments")
    summary = relationship("AssessmentSummary", back_populates="assessment", uselist=False, cascade="all, delete-orphan")
    calculations = relationship("CarbonCalculation", back_populates="assessment", cascade="all, delete-orphan")
    reduction_contributions = relationship("CarbonReductionContribution", back_populates="assessment", cascade="all, delete-orphan")
    scenarios = relationship("Scenario", back_populates="assessment", cascade="all, delete-orphan")
    reports = relationship("ReportRecord", back_populates="assessment", cascade="all, delete-orphan")

class AssessmentSummary(Base):
    __tablename__ = "assessment_summaries"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), unique=True, nullable=False)
    
    # Scope 1, 2, 3 in tCO2e
    scope1 = Column(Float, default=0.0)
    scope2 = Column(Float, default=0.0)
    scope3 = Column(Float, default=0.0)

    # 3 Fundamental Pillars (in tCO2e)
    gross_emissions = Column(Float, default=0.0)
    eligible_reductions = Column(Float, default=0.0)
    net_footprint = Column(Float, default=0.0)
    sequestration = Column(Float, default=0.0)

    # Populations and Intensities
    population = Column(Integer, default=0)
    gross_per_person = Column(Float, default=0.0)
    reduction_per_person = Column(Float, default=0.0)
    net_per_person = Column(Float, default=0.0)

    # Built-up Area and Intensities (per sqm)
    built_up_area_sqm = Column(Float, default=0.0)
    gross_per_area = Column(Float, default=0.0)
    reduction_per_area = Column(Float, default=0.0)
    net_per_area = Column(Float, default=0.0)

    # Key Performance Indicators
    renewable_percentage = Column(Float, default=0.0)
    grid_electricity_displaced_kwh = Column(Float, default=0.0)
    total_energy_consumption_kwh = Column(Float, default=0.0)
    total_water_consumption_kl = Column(Float, default=0.0)
    total_waste_generated_kg = Column(Float, default=0.0)
    waste_diversion_rate = Column(Float, default=0.0)

    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    assessment = relationship("Assessment", back_populates="summary")

class ReportRecord(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    report_type = Column(String(50), nullable=False) # PDF, Excel, CSV
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    generated_at = Column(DateTime, default=datetime.datetime.utcnow)

    assessment = relationship("Assessment", back_populates="reports")
