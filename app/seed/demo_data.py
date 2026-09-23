import datetime
from sqlalchemy.orm import Session
from app.models.organization import Organization, User
from app.models.campus import Campus, Building, Occupancy
from app.models.assessment import Assessment, AssessmentSummary
from app.models.activity import (
    EnergyRecord, RenewableRecord, Vehicle, TransportRecord,
    WasteRecord, WaterRecord, WastewaterRecord, GreenRecord,
    WaterConservationRecord, WaterBodyRecord, AnimalRecord,
    FoodRecord, IndustrialRecord
)
from app.models.carbon import EmissionFactor, CarbonCalculation, CarbonReductionContribution
from app.models.scenario import Recommendation

def seed_demo_data(db: Session):
    # 1. Organization
    org = db.query(Organization).filter(Organization.name == "Christ University").first()
    if not org:
        org = Organization(
            name="Christ University",
            contact_email="sustainability@christuniversity.in",
            contact_phone="+91-80-4012-9100",
            address="Hosur Road, Bengaluru, Karnataka 560029, India"
        )
        db.add(org)
        db.flush()

    # 2. Users
    user = db.query(User).filter(User.email == "admin@christuniversity.in").first()
    if not user:
        user = User(
            organization_id=org.id,
            name="Campus Sustainability Officer",
            email="admin@christuniversity.in",
            password_hash="admin123",
            role="ADMIN",
            active=True
        )
        db.add(user)

    # 3. Kengeri Campus (Requirement 28 Example Data)
    campus = db.query(Campus).filter(Campus.name == "Christ University – Kengeri Campus").first()
    if not campus:
        area_acres = 78.5
        area_sqm = area_acres * 4046.856 # 317,678.2 m²
        built_up_pct = 55.0
        calc_built_up_acres = area_acres * (built_up_pct / 100.0) # 43.175 acres
        calc_built_up_sqm = 174750.0 # Standardized 174,750 m²

        students_on = 900
        students_off = 5100
        faculty = 300
        non_teaching = 150
        total_student_pop = students_on + students_off # 6000
        total_staff_pop = faculty + non_teaching # 450
        total_pop = total_student_pop + total_staff_pop # 6450
        num_blds = 19

        campus = Campus(
            organization_id=org.id,
            name="Christ University – Kengeri Campus",
            campus_type="University / College",
            country="India",
            state="Karnataka",
            city="Bengaluru",
            address="Kanmanike, Kumbalgodu, Mysuru Road, Bengaluru, Karnataka 560074",
            area=area_acres,
            area_unit="Acres",
            area_sqm=round(area_sqm, 2),
            built_up_percentage=built_up_pct,
            calculated_built_up_area_acres=round(calc_built_up_acres, 2),
            calculated_built_up_area_sqm=calc_built_up_sqm,
            total_built_up_area_sqm=calc_built_up_sqm,
            operating_days_per_year=280,
            operating_hours_per_day=8.0,
            assessment_year=2025,
            students_on_campus=students_on,
            students_off_campus=students_off,
            faculty_count=faculty,
            non_teaching_count=non_teaching,
            total_student_population=total_student_pop,
            total_staff_population=total_staff_pop,
            population=total_pop,
            num_buildings=num_blds,
            negative_activities={
                "solar_plant": True,
                "water_conservation": False,
                "water_bodies": True,
                "animals": False,
                "gardening": True
            },
            config={
                "energy": True, "solar": True, "fleet": True, "ev": True,
                "waste": True, "water": True, "wastewater": True,
                "canteens": True, "greenery": True, "industry": False
            }
        )
        db.add(campus)
        db.flush()

        # Define Exactly 19 Buildings (Code, Name, Type, Floors, Area m², Occ, On, Off, Fac, Non)
        building_defs = [
            ("ENG-01", "Engineering Block I (Civil & Mechanical)", "Academic", 5, 14500.0, 600, 50, 500, 30, 20),
            ("ENG-02", "Engineering Block II (CSE & ECE)", "Academic", 5, 16200.0, 750, 60, 620, 40, 30),
            ("ARCH-01", "School of Architecture & Planning", "Academic", 4, 9800.0, 400, 30, 330, 25, 15),
            ("MGMT-01", "School of Business & Management", "Academic", 4, 11500.0, 550, 40, 460, 30, 20),
            ("ARTS-01", "Social Sciences & Humanities Block", "Academic", 4, 8500.0, 420, 30, 350, 25, 15),
            ("RES-01", "Center for Research & Innovation", "Laboratory", 3, 7200.0, 250, 20, 200, 20, 10),
            ("LIB-01", "Central Knowledge & Library Center", "Library", 3, 7400.0, 300, 20, 250, 15, 15),
            ("AUD-01", "Main Auditorium & Cultural Complex", "Auditorium", 2, 6800.0, 200, 10, 170, 10, 10),
            ("HST-01", "St. Kuriakose Boys Hostel", "Hostel", 6, 12500.0, 250, 240, 0, 5, 5),
            ("HST-02", "Devadan Hall Boys Hostel", "Hostel", 6, 11800.0, 220, 210, 0, 5, 5),
            ("HST-03", "Carmel Hall Girls Hostel", "Hostel", 6, 13200.0, 260, 250, 0, 5, 5),
            ("HST-04", "Mother Teresa Girls Hostel", "Hostel", 6, 12800.0, 210, 200, 0, 5, 5),
            ("QTR-01", "Staff & Faculty Residential Quarters", "Staff Quarters", 4, 8200.0, 90, 0, 0, 50, 40),
            ("SPRT-01", "Indoor Sports Complex & Gymnasium", "Sports / Recreation", 2, 6500.0, 150, 10, 120, 10, 10),
            ("DIN-01", "Central Dining Hall & Food Court", "Canteen / Kitchen", 2, 5500.0, 180, 20, 140, 10, 10),
            ("LAB-01", "Advanced Computing & AI Laboratories", "Laboratory", 3, 6200.0, 220, 20, 180, 10, 10),
            ("LAB-02", "Robotics & IoT Workshop", "Laboratory", 2, 5400.0, 160, 10, 130, 10, 10),
            ("ADM-01", "Central Administrative Block", "Administrative", 4, 7650.0, 240, 0, 180, 20, 40),
            ("MED-01", "Campus Health Center & Clinic", "Hospital / Medical", 2, 7200.0, 100, 0, 70, 15, 15)
        ]

        buildings_map = {}
        for code, bname, btype, flr, area, occ, s_on, s_off, fac, non in building_defs:
            b = Building(
                campus_id=campus.id,
                building_code=code,
                name=bname,
                building_type=btype,
                floors=flr,
                built_up_area=area,
                area_unit="Sq Meters",
                built_up_area_sqm=area,
                students_on_campus=s_on,
                students_off_campus=s_off,
                faculty_count=fac,
                non_teaching_count=non,
                occupancy=occ,
                operating_hours=8.0,
                year_constructed=2012,
                description=f"{bname} at Christ University Kengeri Campus"
            )
            db.add(b)
            db.flush()
            buildings_map[code] = b

        # 4. Create Baseline Assessment 2025
        assessment_2025 = Assessment(
            campus_id=campus.id,
            name="Annual Comprehensive Carbon Footprint Assessment 2025",
            reporting_year=2025,
            start_date="2025-01-01",
            end_date="2025-12-31",
            status="Completed",
            methodology="GHG Protocol Corporate Standard / ISO 14064-1 (India CEA v19 Grid Baseline)",
            boundary_description="Operational Control Boundary covering all 19 buildings, campus fleet, on-site solar, central STP, solid waste, and commuter transit on 78.5 acres.",
            created_by="Sustainability Cell, Christ University"
        )
        db.add(assessment_2025)
        db.flush()

        # 5. Whole-Campus Activity Data
        # A. Electricity: 1,850,000 kWh Grid Electricity (Scope 2)
        db.add(EnergyRecord(
            assessment_id=assessment_2025.id,
            campus_id=campus.id,
            data_scope="Whole Campus",
            energy_type="Grid Electricity",
            source="BESCOM (Karnataka Electricity Board)",
            quantity=1850000.0,
            unit="kWh",
            purpose="Campus Operations",
            data_period="Annual",
            year=2025,
            data_source="Annual BESCOM HT Utility Invoices",
            data_quality="Bill/invoice",
            notes="Active energy consumption for entire campus grid connection"
        ))

        # B. Fuel: 42,000 Liters Diesel for Backup DG Sets (Scope 1)
        db.add(EnergyRecord(
            assessment_id=assessment_2025.id,
            campus_id=campus.id,
            data_scope="Whole Campus",
            energy_type="Diesel",
            source="On-site 500 kVA DG Sets",
            quantity=42000.0,
            unit="Liters",
            purpose="DG Generator",
            data_period="Annual",
            year=2025,
            data_source="Diesel Fuel Logbook & Invoices",
            data_quality="Bill/invoice",
            notes="Campus backup power generation during grid outages"
        ))

        # C. Solid Waste: 82,000 kg Composted + 45,000 kg Recycled + 28,000 kg Landfill
        db.add(WasteRecord(
            assessment_id=assessment_2025.id,
            campus_id=campus.id,
            data_scope="Whole Campus",
            waste_type="Food Waste",
            quantity=82000.0,
            unit="kg",
            disposal_method="Composting",
            data_period="Annual",
            year=2025,
            data_quality="Measured",
            notes="On-site aerobic composting of canteen and horticultural waste"
        ))
        db.add(WasteRecord(
            assessment_id=assessment_2025.id,
            campus_id=campus.id,
            data_scope="Whole Campus",
            waste_type="Paper",
            quantity=45000.0,
            unit="kg",
            disposal_method="Recycling",
            data_period="Annual",
            year=2025,
            data_quality="Measured",
            notes="Authorized closed-loop paper and plastic recycling"
        ))
        db.add(WasteRecord(
            assessment_id=assessment_2025.id,
            campus_id=campus.id,
            data_scope="Whole Campus",
            waste_type="Mixed Waste",
            quantity=28000.0,
            unit="kg",
            disposal_method="Landfill",
            data_period="Annual",
            year=2025,
            data_quality="Measured",
            notes="Residual non-recyclable inert waste to municipal landfill"
        ))

        # D. Water & STP: 145,000 kL Borewell + 35,000 kL Rainwater + 110,000 kL Treated STP
        db.add(WaterRecord(
            assessment_id=assessment_2025.id,
            campus_id=campus.id,
            data_scope="Whole Campus",
            source="Borewell",
            usage_type="Campus Domestic & Hostels",
            quantity=145000.0,
            unit="kL",
            data_period="Annual",
            year=2025,
            data_quality="Flow Meter Reading"
        ))
        db.add(WaterRecord(
            assessment_id=assessment_2025.id,
            campus_id=campus.id,
            data_scope="Whole Campus",
            source="Rainwater",
            usage_type="Recharge & Retention Ponds",
            quantity=35000.0,
            unit="kL",
            data_period="Annual",
            year=2025,
            data_quality="Flow Meter Reading"
        ))
        db.add(WastewaterRecord(
            assessment_id=assessment_2025.id,
            campus_id=campus.id,
            facility_name="Kengeri Campus Central SBR STP",
            treatment_type="SBR STP",
            capacity_kld=500.0,
            wastewater_quantity=110000.0,
            treated_quantity=105000.0,
            reused_quantity=98000.0,
            electricity_kwh=42000.0,
            sludge_kg=6500.0,
            data_period="Annual",
            year=2025,
            data_quality="Measured"
        ))

        # E. Transportation / Fleet: 15 Buses + 2 EV Buggies + Utility Vehicles
        db.add(TransportRecord(
            assessment_id=assessment_2025.id,
            campus_id=campus.id,
            data_scope="Whole Campus",
            record_type="Fleet",
            mode="Bus",
            fuel_type="Diesel",
            vehicle_count=15,
            distance_km=180000.0,
            fuel_quantity=55000.0,
            fuel_unit="Liters",
            passengers=52,
            year=2025,
            data_quality="Fuel Invoice / Log"
        ))
        db.add(TransportRecord(
            assessment_id=assessment_2025.id,
            campus_id=campus.id,
            data_scope="Whole Campus",
            record_type="Fleet",
            mode="Electric Vehicle",
            fuel_type="Electricity",
            vehicle_count=2,
            distance_km=14000.0,
            charging_electricity_kwh=4800.0,
            is_ev_in_grid_electricity=True,
            year=2025,
            data_quality="Meter reading"
        ))

        # F. Canteen: Central Dining Hall LPG
        db.add(FoodRecord(
            assessment_id=assessment_2025.id,
            campus_id=campus.id,
            building_id=buildings_map["DIN-01"].id,
            canteen_name="Central Dining Hall & Food Court",
            operating_days=280,
            meals_served=850000,
            lpg_kg=26000.0,
            electricity_kwh=35000.0,
            food_waste_kg=22000.0,
            water_kl=3500.0,
            year=2025
        ))

        # G. Negative Activities (Selected: Solar Plant, Water Bodies, Gardening)
        # Solar Plant: 500 kWp, 720,000 kWh
        db.add(RenewableRecord(
            assessment_id=assessment_2025.id,
            campus_id=campus.id,
            technology="Solar PV",
            capacity_kw=500.0,
            generation_kwh=720000.0,
            displaced_grid_kwh=720000.0,
            is_onsite_consumed=True,
            installation_location="Campus Academic Rooftops",
            data_quality="Generation Meter",
            year=2025
        ))

        # Water Bodies: 2 Retention Lakes / Ponds (15,000 m²)
        db.add(WaterBodyRecord(
            assessment_id=assessment_2025.id,
            campus_id=campus.id,
            body_count=2,
            total_area_sqm=15000.0,
            body_type="Lake",
            carbon_benefit_tco2e=7.5,
            methodology="Ramsar Wetland Sediment Carbon Stabilization Factor",
            data_quality="GIS Survey",
            year=2025
        ))

        # Gardening / Greenery: 2,800 Trees across 182,000 m²
        db.add(GreenRecord(
            assessment_id=assessment_2025.id,
            campus_id=campus.id,
            green_area_sqm=182000.0,
            tree_count=2800,
            plant_count=5000,
            tree_species="Neem, Teak, Peepal, Mango, Rain Tree, Native evergreen",
            annual_sequestration_tco2e=61.6,
            methodology="FSI Tree Biomass & IPCC Good Practice Guidance (22.0 kg CO2/tree/year)",
            data_quality="Physical Tree Census",
            year=2025
        ))

        db.commit()
        print("Seeded Christ University – Kengeri Campus (19 Buildings, Campus-Centric, 6,450 Population).")
