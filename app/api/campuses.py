from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.organization import Organization
from app.models.campus import Campus, Building, Occupancy
from app.models.assessment import Assessment
from app.schemas.schemas import (
    CampusCreate, CampusOut, BuildingCreate, BuildingOut,
    BuildingPopulationUpdate, OrganizationCreate, OrganizationOut
)

router = APIRouter(prefix="/api/campuses", tags=["Campuses & Buildings"])

@router.get("/organizations", response_model=list[OrganizationOut])
def list_organizations(db: Session = Depends(get_db)):
    return db.query(Organization).all()

@router.post("/organizations", response_model=OrganizationOut)
def create_organization(org_in: OrganizationCreate, db: Session = Depends(get_db)):
    org = Organization(**org_in.dict())
    db.add(org)
    db.commit()
    db.refresh(org)
    return org

@router.get("/", response_model=list[CampusOut])
def list_campuses(db: Session = Depends(get_db)):
    return db.query(Campus).all()

@router.get("/{campus_id}", response_model=CampusOut)
def get_campus(campus_id: int, db: Session = Depends(get_db)):
    campus = db.query(Campus).filter(Campus.id == campus_id).first()
    if not campus:
        raise HTTPException(status_code=404, detail="Campus not found")
    return campus

@router.post("/", response_model=CampusOut)
def create_campus(campus_in: CampusCreate, db: Session = Depends(get_db)):
    # 1. Guarantee Organization Exists
    org = db.query(Organization).filter(Organization.id == campus_in.organization_id).first()
    if not org:
        org = db.query(Organization).first()
        if not org:
            org = Organization(name="Default Organization", contact_email="admin@campuscarbon.org")
            db.add(org)
            db.flush()
        campus_in.organization_id = org.id

    # 2. Convert Area Units (1 acre = 4046.856 m²)
    area_unit = campus_in.area_unit or "Acres"
    if area_unit.lower() == "acres":
        area_acres = campus_in.area
        area_sqm = campus_in.area * 4046.856
    else:
        area_sqm = campus_in.area
        area_acres = campus_in.area / 4046.856

    # 3. Built-up Area Calculation (Total Campus Area * Built-up % / 100)
    built_up_pct = max(0.0, min(100.0, campus_in.built_up_percentage))
    calc_built_up_acres = area_acres * (built_up_pct / 100.0)
    calc_built_up_sqm = area_sqm * (built_up_pct / 100.0)

    # 4. Population Totals (Auto-calculated)
    students_on = max(0, campus_in.students_on_campus)
    students_off = max(0, campus_in.students_off_campus)
    faculty = max(0, campus_in.faculty_count)
    non_teaching = max(0, campus_in.non_teaching_count)
    
    total_student_pop = students_on + students_off
    total_staff_pop = faculty + non_teaching
    total_pop = total_student_pop + total_staff_pop

    num_blds = max(1, campus_in.num_buildings or len(campus_in.buildings or []))

    # 5. Negative Activities Checklist Default
    neg_act = campus_in.negative_activities or {
        "water_conservation": False,
        "solar_plant": True,
        "water_bodies": False,
        "animals": False,
        "gardening": True
    }

    campus = Campus(
        organization_id=campus_in.organization_id,
        name=campus_in.name,
        campus_type=campus_in.campus_type,
        country=campus_in.country or "India",
        state=campus_in.state,
        city=campus_in.city,
        address=campus_in.address,
        area=area_acres if area_unit.lower() == "acres" else area_sqm,
        area_unit=area_unit,
        area_sqm=round(area_sqm, 2),
        built_up_percentage=round(built_up_pct, 2),
        calculated_built_up_area_acres=round(calc_built_up_acres, 2),
        calculated_built_up_area_sqm=round(calc_built_up_sqm, 2),
        total_built_up_area_sqm=round(calc_built_up_sqm, 2),
        operating_days_per_year=campus_in.operating_days_per_year or 280,
        operating_hours_per_day=campus_in.operating_hours_per_day or 8.0,
        assessment_year=campus_in.assessment_year or 2025,
        students_on_campus=students_on,
        students_off_campus=students_off,
        faculty_count=faculty,
        non_teaching_count=non_teaching,
        total_student_population=total_student_pop,
        total_staff_population=total_staff_pop,
        population=total_pop,
        num_buildings=num_blds,
        negative_activities=neg_act,
        config=campus_in.config or {}
    )
    db.add(campus)
    db.flush()

    # 6. Generate EXACTLY num_buildings records
    buildings_data = campus_in.buildings or []
    default_types = ["Academic", "Administrative", "Hostel", "Library", "Auditorium", "Laboratory", "Canteen / Kitchen", "Sports / Recreation"]
    
    total_bld_sqm = 0.0
    for i in range(num_blds):
        if i < len(buildings_data):
            b_in = buildings_data[i]
            b_code = b_in.building_code or f"BLD-{i+1:02d}"
            b_name = b_in.name or f"Building {i+1}"
            b_type = b_in.building_type or default_types[i % len(default_types)]
            b_area = b_in.built_up_area if b_in.built_up_area > 0 else round(calc_built_up_sqm / num_blds, 2)
            b_floors = b_in.floors or 3
            b_desc = b_in.description
        else:
            b_code = f"BLD-{i+1:02d}"
            b_name = f"Campus Block {i+1}"
            b_type = default_types[i % len(default_types)]
            b_area = round(calc_built_up_sqm / num_blds, 2)
            b_floors = 3
            b_desc = None

        area_sqm = b_area
        total_bld_sqm += area_sqm
        bld = Building(
            campus_id=campus.id,
            building_code=b_code,
            name=b_name,
            building_type=b_type,
            floors=b_floors,
            built_up_area=b_area,
            area_unit="Sq Meters",
            built_up_area_sqm=area_sqm,
            occupancy=round(total_pop / num_blds),
            students_on_campus=round(students_on / num_blds),
            students_off_campus=round(students_off / num_blds),
            faculty_count=round(faculty / num_blds),
            non_teaching_count=round(non_teaching / num_blds),
            operating_hours=campus.operating_hours_per_day,
            description=b_desc
        )
        db.add(bld)

    campus.total_built_up_area_sqm = round(total_bld_sqm, 2)
    db.commit()
    db.refresh(campus)
    return campus

@router.get("/{campus_id}/buildings", response_model=list[BuildingOut])
def list_buildings(campus_id: int, db: Session = Depends(get_db)):
    return db.query(Building).filter(Building.campus_id == campus_id).all()

@router.put("/{campus_id}/buildings/sync", response_model=list[BuildingOut])
def sync_campus_buildings(campus_id: int, buildings_in: list[BuildingCreate], db: Session = Depends(get_db)):
    campus = db.query(Campus).filter(Campus.id == campus_id).first()
    if not campus:
        raise HTTPException(status_code=404, detail="Campus not found")

    # Strict rule: building count must equal campus.num_buildings
    target_count = len(buildings_in)
    campus.num_buildings = target_count

    # Clear and re-populate exactly target_count buildings
    db.query(Building).filter(Building.campus_id == campus_id).delete()
    db.flush()

    total_area = 0.0
    for i, b_in in enumerate(buildings_in):
        area_sqm = b_in.built_up_area
        total_area += area_sqm
        bld = Building(
            campus_id=campus.id,
            building_code=b_in.building_code or f"BLD-{i+1:02d}",
            name=b_in.name or f"Building {i+1}",
            building_type=b_in.building_type or "Academic",
            floors=b_in.floors or 1,
            built_up_area=b_in.built_up_area or 0.0,
            area_unit="Sq Meters",
            built_up_area_sqm=area_sqm,
            students_on_campus=b_in.students_on_campus or 0,
            students_off_campus=b_in.students_off_campus or 0,
            faculty_count=b_in.faculty_count or 0,
            non_teaching_count=b_in.non_teaching_count or 0,
            occupancy=b_in.occupancy or (b_in.students_on_campus + b_in.faculty_count + b_in.non_teaching_count),
            operating_hours=b_in.operating_hours or 8.0,
            year_constructed=b_in.year_constructed,
            description=b_in.description
        )
        db.add(bld)

    campus.total_built_up_area_sqm = round(total_area, 2)
    db.commit()
    return db.query(Building).filter(Building.campus_id == campus_id).all()

@router.post("/{campus_id}/buildings/population")
def update_building_population(campus_id: int, pop_updates: list[BuildingPopulationUpdate], db: Session = Depends(get_db)):
    campus = db.query(Campus).filter(Campus.id == campus_id).first()
    if not campus:
        raise HTTPException(status_code=404, detail="Campus not found")

    total_allocated = 0
    for p in pop_updates:
        bld = db.query(Building).filter(Building.id == p.building_id, Building.campus_id == campus_id).first()
        if bld:
            bld.students_on_campus = p.students_on_campus
            bld.students_off_campus = p.students_off_campus
            bld.faculty_count = p.faculty_count
            bld.non_teaching_count = p.non_teaching_count
            bld.other_occupants = p.other_occupants
            bld.occupancy = p.students_on_campus + p.students_off_campus + p.faculty_count + p.non_teaching_count + p.other_occupants
            total_allocated += bld.occupancy

    db.commit()
    return {
        "success": True,
        "total_allocated": total_allocated,
        "campus_population": campus.population,
        "matches": total_allocated == campus.population
    }
