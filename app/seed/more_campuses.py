import datetime
from sqlalchemy.orm import Session
from app.models.organization import Organization, User
from app.models.campus import Campus, Building, Occupancy
from app.models.assessment import Assessment, AssessmentSummary
from app.models.activity import (
    EnergyRecord, RenewableRecord, Vehicle, TransportRecord,
    WasteRecord, WaterRecord, WastewaterRecord, GreenRecord,
    FoodRecord, IndustrialRecord
)
from app.engine.carbon_calculator import calculate_gross_emissions
from app.engine.reduction_calculator import calculate_reduction_contributions
from app.engine.aggregator import aggregate_assessment_summary

def seed_additional_campuses(db: Session):
    org = db.query(Organization).first()
    if not org:
        return

    # 1. Greenwood International High School
    c_school = db.query(Campus).filter(Campus.name == "Greenwood International School").first()
    if not c_school:
        c_school = Campus(
            organization_id=org.id,
            name="Greenwood International School",
            campus_type="School",
            country="India",
            state="Karnataka",
            city="Bengaluru",
            address="Sarjapur Road, Bengaluru, Karnataka 560087",
            area=15.0,
            area_unit="Acres",
            population=1800,
            total_built_up_area_sqm=28000.0,
            config={"energy": True, "solar": True, "fleet": True, "waste": True, "water": True, "greenery": True}
        )
        db.add(c_school)
        db.flush()

        # Buildings
        b1 = Building(campus_id=c_school.id, building_code="SCH-PR", name="Primary Academic Wing", building_type="Academic", floors=3, built_up_area_sqm=9500, occupancy=700, operating_hours=7.0, year_constructed=2015)
        b2 = Building(campus_id=c_school.id, building_code="SCH-SEC", name="Secondary & Senior Wing", building_type="Academic", floors=3, built_up_area_sqm=11000, occupancy=850, operating_hours=7.5, year_constructed=2016)
        b3 = Building(campus_id=c_school.id, building_code="SCH-ADM", name="Administration & Auditorium", building_type="Admin", floors=2, built_up_area_sqm=4500, occupancy=150, operating_hours=8.0, year_constructed=2015)
        b4 = Building(campus_id=c_school.id, building_code="SCH-SPT", name="Indoor Sports Complex", building_type="Sports", floors=2, built_up_area_sqm=3000, occupancy=100, operating_hours=5.0, year_constructed=2018)
        db.add_all([b1, b2, b3, b4])
        db.flush()

        asm_school = Assessment(
            campus_id=c_school.id,
            name="School Carbon Audit 2025",
            reporting_year=2025,
            status="Completed",
            methodology="GHG Protocol Corporate Standard (School Boundary)"
        )
        db.add(asm_school)
        db.flush()

        # Activity
        db.add(EnergyRecord(assessment_id=asm_school.id, campus_id=c_school.id, building_id=b1.id, energy_type="Grid Electricity", quantity=140000.0, unit="kWh", year=2025))
        db.add(EnergyRecord(assessment_id=asm_school.id, campus_id=c_school.id, building_id=b2.id, energy_type="Grid Electricity", quantity=165000.0, unit="kWh", year=2025))
        db.add(RenewableRecord(assessment_id=asm_school.id, campus_id=c_school.id, building_id=b2.id, technology="Solar PV", capacity_kw=100.0, generation_kwh=145000.0, displaced_grid_kwh=145000.0, is_onsite_consumed=True, year=2025))
        db.add(TransportRecord(assessment_id=asm_school.id, campus_id=c_school.id, record_type="Fleet", mode="School Buses (8 units)", fuel_type="Diesel", fuel_quantity=18000.0, fuel_unit="Liters", year=2025))
        db.add(WasteRecord(assessment_id=asm_school.id, campus_id=c_school.id, waste_type="Organic & Cafeteria Waste", quantity=18000.0, unit="kg", disposal_method="Composting", year=2025))
        db.add(WasteRecord(assessment_id=asm_school.id, campus_id=c_school.id, waste_type="Paper & Craft Recyclables", quantity=9500.0, unit="kg", disposal_method="Recycling", year=2025))
        db.add(GreenRecord(assessment_id=asm_school.id, campus_id=c_school.id, green_area_sqm=28000.0, tree_count=450, annual_sequestration_tco2e=9.9, year=2025))
        db.flush()

        calculate_gross_emissions(db, asm_school.id)
        calculate_reduction_contributions(db, asm_school.id)
        aggregate_assessment_summary(db, asm_school.id)

    # 2. Palm Meadows Residential Society
    c_apt = db.query(Campus).filter(Campus.name == "Palm Meadows Residential Society").first()
    if not c_apt:
        c_apt = Campus(
            organization_id=org.id,
            name="Palm Meadows Residential Society",
            campus_type="Apartment Society",
            country="India",
            state="Karnataka",
            city="Bengaluru",
            address="Whitefield, Bengaluru, Karnataka 560066",
            area=40.0,
            area_unit="Acres",
            population=2200,
            total_built_up_area_sqm=95000.0,
            config={"energy": True, "solar": True, "waste": True, "water": True, "wastewater": True, "greenery": True, "ev": True}
        )
        db.add(c_apt)
        db.flush()

        # Towers
        for i in range(1, 9):
            db.add(Building(
                campus_id=c_apt.id,
                building_code=f"TWR-{i:02d}",
                name=f"Residential Tower {chr(64+i)}",
                building_type="Residential",
                floors=14,
                built_up_area_sqm=11000.0,
                occupancy=260,
                operating_hours=24.0,
                year_constructed=2018
            ))
        db.flush()

        asm_apt = Assessment(
            campus_id=c_apt.id,
            name="Residential Community Carbon Assessment 2025",
            reporting_year=2025,
            status="Completed",
            methodology="GHG Protocol Gated Community / Apartment Standard"
        )
        db.add(asm_apt)
        db.flush()

        # Common electricity & DG
        db.add(EnergyRecord(assessment_id=asm_apt.id, campus_id=c_apt.id, energy_type="Grid Electricity", source="Common Services Grid", quantity=850000.0, unit="kWh", year=2025))
        db.add(EnergyRecord(assessment_id=asm_apt.id, campus_id=c_apt.id, energy_type="Diesel Generator", source="Backup DG", quantity=22000.0, unit="Liters", year=2025))
        db.add(RenewableRecord(assessment_id=asm_apt.id, campus_id=c_apt.id, technology="Solar PV", capacity_kw=150.0, generation_kwh=210000.0, displaced_grid_kwh=210000.0, is_onsite_consumed=True, year=2025))
        db.add(TransportRecord(assessment_id=asm_apt.id, campus_id=c_apt.id, record_type="EV Charging", mode="Resident EV Charging Stations (6 hubs)", fuel_type="Electricity", charging_electricity_kwh=42000.0, year=2025))
        db.add(WasteRecord(assessment_id=asm_apt.id, campus_id=c_apt.id, waste_type="Wet Organic Waste", quantity=110000.0, unit="kg", disposal_method="Composting", year=2025))
        db.add(WasteRecord(assessment_id=asm_apt.id, campus_id=c_apt.id, waste_type="Dry Recyclables", quantity=45000.0, unit="kg", disposal_method="Recycling", year=2025))
        db.add(WastewaterRecord(assessment_id=asm_apt.id, campus_id=c_apt.id, facility_name="Community SBR STP", treatment_type="STP", capacity_kld=300.0, wastewater_quantity=75000.0, treated_quantity=72000.0, reused_quantity=68000.0, year=2025))
        db.add(GreenRecord(assessment_id=asm_apt.id, campus_id=c_apt.id, green_area_sqm=65000.0, tree_count=620, annual_sequestration_tco2e=13.64, year=2025))
        db.flush()

        calculate_gross_emissions(db, asm_apt.id)
        calculate_reduction_contributions(db, asm_apt.id)
        aggregate_assessment_summary(db, asm_apt.id)

    # 3. Apex Multi-Specialty Hospital
    c_hosp = db.query(Campus).filter(Campus.name == "Apex Multi-Specialty Hospital").first()
    if not c_hosp:
        c_hosp = Campus(
            organization_id=org.id,
            name="Apex Multi-Specialty Hospital",
            campus_type="Hospital",
            country="India",
            state="Karnataka",
            city="Bengaluru",
            address="Bannerghatta Road, Bengaluru, Karnataka 560076",
            area=12.0,
            area_unit="Acres",
            population=1400,
            total_built_up_area_sqm=42000.0,
            config={"energy": True, "solar": True, "fleet": True, "waste": True, "water": True, "wastewater": True, "greenery": True, "industry": False}
        )
        db.add(c_hosp)
        db.flush()

        b_h1 = Building(campus_id=c_hosp.id, building_code="HOSP-IPD", name="In-Patient Tower & ICU Complex", building_type="Hospital Ward", floors=8, built_up_area_sqm=22000, occupancy=750, operating_hours=24.0, year_constructed=2019)
        b_h2 = Building(campus_id=c_hosp.id, building_code="HOSP-OPD", name="Out-Patient & Diagnostic Center", building_type="Clinical", floors=5, built_up_area_sqm=14000, occupancy=500, operating_hours=14.0, year_constructed=2019)
        b_h3 = Building(campus_id=c_hosp.id, building_code="HOSP-ADM", name="Admin & Central Services", building_type="Admin", floors=3, built_up_area_sqm=6000, occupancy=150, operating_hours=12.0, year_constructed=2020)
        db.add_all([b_h1, b_h2, b_h3])
        db.flush()

        asm_hosp = Assessment(
            campus_id=c_hosp.id,
            name="Hospital Carbon & Environmental Audit 2025",
            reporting_year=2025,
            status="Completed",
            methodology="GHG Protocol Healthcare Standard"
        )
        db.add(asm_hosp)
        db.flush()

        db.add(EnergyRecord(assessment_id=asm_hosp.id, campus_id=c_hosp.id, building_id=b_h1.id, energy_type="Grid Electricity", quantity=920000.0, unit="kWh", year=2025))
        db.add(EnergyRecord(assessment_id=asm_hosp.id, campus_id=c_hosp.id, building_id=b_h2.id, energy_type="Grid Electricity", quantity=480000.0, unit="kWh", year=2025))
        db.add(EnergyRecord(assessment_id=asm_hosp.id, campus_id=c_hosp.id, energy_type="Diesel Generator", quantity=35000.0, unit="Liters", year=2025))
        db.add(TransportRecord(assessment_id=asm_hosp.id, campus_id=c_hosp.id, record_type="Fleet", mode="Emergency ICU Ambulances (4 units)", fuel_type="Diesel", fuel_quantity=14000.0, fuel_unit="Liters", year=2025))
        db.add(WasteRecord(assessment_id=asm_hosp.id, campus_id=c_hosp.id, waste_type="Biomedical waste", quantity=24000.0, unit="kg", disposal_method="Incineration", year=2025))
        db.add(WasteRecord(assessment_id=asm_hosp.id, campus_id=c_hosp.id, waste_type="General non-infectious waste", quantity=38000.0, unit="kg", disposal_method="Landfill", year=2025))
        db.add(GreenRecord(assessment_id=asm_hosp.id, campus_id=c_hosp.id, green_area_sqm=15000.0, tree_count=220, annual_sequestration_tco2e=4.84, year=2025))
        db.flush()

        calculate_gross_emissions(db, asm_hosp.id)
        calculate_reduction_contributions(db, asm_hosp.id)
        aggregate_assessment_summary(db, asm_hosp.id)

    # 4. Precision Heavy Engineering Plant
    c_ind = db.query(Campus).filter(Campus.name == "Precision Heavy Engineering Plant").first()
    if not c_ind:
        c_ind = Campus(
            organization_id=org.id,
            name="Precision Heavy Engineering Plant",
            campus_type="Industrial",
            country="India",
            state="Karnataka",
            city="Bengaluru",
            address="Peenya Industrial Area Phase 2, Bengaluru, Karnataka 560058",
            area=30.0,
            area_unit="Acres",
            population=850,
            total_built_up_area_sqm=55000.0,
            config={"energy": True, "solar": True, "fleet": True, "waste": True, "water": True, "wastewater": True, "industry": True, "greenery": True}
        )
        db.add(c_ind)
        db.flush()

        b_i1 = Building(campus_id=c_ind.id, building_code="PLT-FDY", name="Foundry & Heat Treatment Shop", building_type="Workshop", floors=1, built_up_area_sqm=20000, occupancy=250, operating_hours=16.0, year_constructed=2012)
        b_i2 = Building(campus_id=c_ind.id, building_code="PLT-MCH", name="Precision CNC Machining Bay", building_type="Workshop", floors=1, built_up_area_sqm=18000, occupancy=300, operating_hours=16.0, year_constructed=2014)
        b_i3 = Building(campus_id=c_ind.id, building_code="PLT-ASY", name="Final Assembly & Testing", building_type="Workshop", floors=2, built_up_area_sqm=12000, occupancy=200, operating_hours=10.0, year_constructed=2016)
        b_i4 = Building(campus_id=c_ind.id, building_code="PLT-ADM", name="Plant Admin & Design Center", building_type="Office", floors=3, built_up_area_sqm=5000, occupancy=100, operating_hours=9.0, year_constructed=2012)
        db.add_all([b_i1, b_i2, b_i3, b_i4])
        db.flush()

        asm_ind = Assessment(
            campus_id=c_ind.id,
            name="Industrial Plant GHG Protocol Assessment 2025",
            reporting_year=2025,
            status="Completed",
            methodology="GHG Protocol Corporate / Manufacturing Process Standard"
        )
        db.add(asm_ind)
        db.flush()

        db.add(EnergyRecord(assessment_id=asm_ind.id, campus_id=c_ind.id, building_id=b_i1.id, energy_type="Natural Gas", source="GAIL Gas Pipeline", quantity=120000.0, unit="m3", year=2025))
        db.add(EnergyRecord(assessment_id=asm_ind.id, campus_id=c_ind.id, building_id=b_i2.id, energy_type="Grid Electricity", quantity=1650000.0, unit="kWh", year=2025))
        db.add(EnergyRecord(assessment_id=asm_ind.id, campus_id=c_ind.id, energy_type="Diesel Generator", quantity=48000.0, unit="Liters", year=2025))
        db.add(IndustrialRecord(assessment_id=asm_ind.id, campus_id=c_ind.id, production_name="Precision Turbine Castings", production_quantity=4500.0, production_unit="Tonnes", process_emissions_tco2e=185.0, refrigerant_leakage_kg=25.0, year=2025))
        db.add(RenewableRecord(assessment_id=asm_ind.id, campus_id=c_ind.id, technology="Solar PV", capacity_kw=350.0, generation_kwh=490000.0, displaced_grid_kwh=490000.0, is_onsite_consumed=True, year=2025))
        db.add(WasteRecord(assessment_id=asm_ind.id, campus_id=c_ind.id, waste_type="Industrial Metal Scrap", quantity=140000.0, unit="kg", disposal_method="Recycling", year=2025))
        db.add(GreenRecord(assessment_id=asm_ind.id, campus_id=c_ind.id, green_area_sqm=35000.0, tree_count=520, annual_sequestration_tco2e=11.44, year=2025))
        db.flush()

        calculate_gross_emissions(db, asm_ind.id)
        calculate_reduction_contributions(db, asm_ind.id)
        aggregate_assessment_summary(db, asm_ind.id)

    # 5. TechnoPark Corporate Hub
    c_corp = db.query(Campus).filter(Campus.name == "TechnoPark Corporate Hub").first()
    if not c_corp:
        c_corp = Campus(
            organization_id=org.id,
            name="TechnoPark Corporate Hub",
            campus_type="Office / Corporate",
            country="India",
            state="Karnataka",
            city="Bengaluru",
            address="Outer Ring Road, Bellandur, Bengaluru, Karnataka 560103",
            area=18.0,
            area_unit="Acres",
            population=4500,
            total_built_up_area_sqm=75000.0,
            config={"energy": True, "solar": True, "fleet": True, "waste": True, "water": True, "wastewater": True, "greenery": True, "ev": True}
        )
        db.add(c_corp)
        db.flush()

        for i in range(1, 6):
            db.add(Building(
                campus_id=c_corp.id,
                building_code=f"TECH-{i:02d}",
                name=f"IT Tower {i}",
                building_type="Office",
                floors=9,
                built_up_area_sqm=15000.0,
                occupancy=900,
                operating_hours=14.0,
                year_constructed=2021
            ))
        db.flush()

        asm_corp = Assessment(
            campus_id=c_corp.id,
            name="TechnoPark Annual ESG Carbon Assessment 2025",
            reporting_year=2025,
            status="Completed",
            methodology="GHG Protocol Corporate Standard (Scope 1, 2, 3 Market & Location Based)"
        )
        db.add(asm_corp)
        db.flush()

        db.add(EnergyRecord(assessment_id=asm_corp.id, campus_id=c_corp.id, energy_type="Grid Electricity", quantity=2100000.0, unit="kWh", year=2025))
        db.add(EnergyRecord(assessment_id=asm_corp.id, campus_id=c_corp.id, energy_type="Diesel Generator", quantity=28000.0, unit="Liters", year=2025))
        db.add(RenewableRecord(assessment_id=asm_corp.id, campus_id=c_corp.id, technology="Solar PV", capacity_kw=400.0, generation_kwh=580000.0, displaced_grid_kwh=580000.0, is_onsite_consumed=True, year=2025))
        db.add(TransportRecord(assessment_id=asm_corp.id, campus_id=c_corp.id, record_type="EV Charging", mode="Employee EV Fast Charging Stations", fuel_type="Electricity", charging_electricity_kwh=85000.0, year=2025))
        db.add(TransportRecord(assessment_id=asm_corp.id, campus_id=c_corp.id, record_type="Commuting", mode="Employee Metro & Transit Commute", fuel_type="Public Transit", distance_km=3200000.0, year=2025))
        db.add(WasteRecord(assessment_id=asm_corp.id, campus_id=c_corp.id, waste_type="Dry Recyclables (E-waste, Paper)", quantity=65000.0, unit="kg", disposal_method="Recycling", year=2025))
        db.add(WasteRecord(assessment_id=asm_corp.id, campus_id=c_corp.id, waste_type="Cafeteria Food Waste", quantity=42000.0, unit="kg", disposal_method="Composting", year=2025))
        db.add(GreenRecord(assessment_id=asm_corp.id, campus_id=c_corp.id, green_area_sqm=32000.0, tree_count=480, annual_sequestration_tco2e=10.56, year=2025))
        db.flush()

        calculate_gross_emissions(db, asm_corp.id)
        calculate_reduction_contributions(db, asm_corp.id)
        aggregate_assessment_summary(db, asm_corp.id)

    db.commit()
    print("Additional 5 campus archetypes seeded and calculated successfully.")
