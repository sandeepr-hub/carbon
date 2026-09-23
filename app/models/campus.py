import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class Campus(Base):
    __tablename__ = "campuses"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    name = Column(String(255), nullable=False)
    campus_type = Column(String(100), nullable=False) # University / College, School, Hospital, Apartment / Residential Society, Industry, Corporate Campus, Research Institution, Other
    country = Column(String(100), default="India")
    state = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    
    # Area & Geometry
    area = Column(Float, default=0.0) # Campus area
    area_unit = Column(String(50), default="Acres") # Acres, m²
    area_sqm = Column(Float, default=0.0) # Standardized area in m²
    built_up_percentage = Column(Float, default=50.0) # % of campus area built-up
    calculated_built_up_area_acres = Column(Float, default=0.0)
    calculated_built_up_area_sqm = Column(Float, default=0.0) # Total Campus Area * Built-up % / 100
    total_built_up_area_sqm = Column(Float, default=0.0) # sum of building areas

    # Operating parameters
    operating_days_per_year = Column(Integer, default=280)
    operating_hours_per_day = Column(Float, default=8.0)
    assessment_year = Column(Integer, default=2025)

    # Population Breakdown
    students_on_campus = Column(Integer, default=0)
    students_off_campus = Column(Integer, default=0)
    faculty_count = Column(Integer, default=0)
    non_teaching_count = Column(Integer, default=0)
    total_student_population = Column(Integer, default=0)
    total_staff_population = Column(Integer, default=0)
    population = Column(Integer, default=0) # Total campus population

    # Building count constraint
    num_buildings = Column(Integer, default=1)

    # Negative activities checklist
    # e.g., {"water_conservation": true, "solar_plant": true, "water_bodies": true, "animals": false, "gardening": true}
    negative_activities = Column(JSON, default=dict)
    config = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    organization = relationship("Organization", back_populates="campuses")
    buildings = relationship("Building", back_populates="campus", cascade="all, delete-orphan")
    assessments = relationship("Assessment", back_populates="campus", cascade="all, delete-orphan")
    vehicles = relationship("Vehicle", back_populates="campus", cascade="all, delete-orphan")
    occupancy_records = relationship("Occupancy", back_populates="campus", cascade="all, delete-orphan")

class Building(Base):
    __tablename__ = "buildings"

    id = Column(Integer, primary_key=True, index=True)
    campus_id = Column(Integer, ForeignKey("campuses.id"), nullable=False)
    building_code = Column(String(50), nullable=True) # Unique identifier
    name = Column(String(255), nullable=False)
    building_type = Column(String(100), nullable=False) # Academic, Administrative, Hostel, Library, Auditorium, Laboratory, Sports / Recreation, Staff Quarters, Canteen / Kitchen, Hospital / Medical, Other
    floors = Column(Integer, default=1)
    built_up_area = Column(Float, default=0.0)
    area_unit = Column(String(50), default="Sq Meters") # Sq Meters
    built_up_area_sqm = Column(Float, default=0.0) # standardized to sqm for calculations
    
    # Building Population Allocation
    students_on_campus = Column(Integer, default=0)
    students_off_campus = Column(Integer, default=0)
    faculty_count = Column(Integer, default=0)
    non_teaching_count = Column(Integer, default=0)
    other_occupants = Column(Integer, default=0)
    occupancy = Column(Integer, default=0) # total building population

    operating_hours = Column(Float, default=8.0) # hours/day
    year_constructed = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)

    campus = relationship("Campus", back_populates="buildings")
    occupancy_records = relationship("Occupancy", back_populates="building", cascade="all, delete-orphan")

class Occupancy(Base):
    __tablename__ = "occupancy"

    id = Column(Integer, primary_key=True, index=True)
    campus_id = Column(Integer, ForeignKey("campuses.id"), nullable=False)
    building_id = Column(Integer, ForeignKey("buildings.id"), nullable=True)
    category = Column(String(100), nullable=False) # Students, Faculty, Staff, Residents, Patients, Guests, Visitors, Workers, Other
    count = Column(Integer, default=0)
    period = Column(String(50), default="Annual") # Annual, Daily, Peak

    campus = relationship("Campus", back_populates="occupancy_records")
    building = relationship("Building", back_populates="occupancy_records")
