import csv
from io import StringIO
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.activity import EnergyRecord, WasteRecord, WaterRecord, TransportRecord
from app.models.campus import Building

def generate_activity_csv_template(module_type: str) -> str:
    templates = {
        "energy": "building_code,energy_type,source,quantity,unit,month,year,data_quality,notes\nENG-01,Grid Electricity,State Grid,210000,kWh,1,2025,Bill/invoice,Monthly utility bill\nENG-01,Diesel Generator,On-site DG,3500,Liters,1,2025,Measured,DG fuel consumption",
        "waste": "building_code,waste_type,quantity,unit,disposal_method,month,year,data_quality,notes\nENG-01,Food waste,4500,kg,Composting,1,2025,Measured,Cafeteria organic waste\nENG-01,Dry Recyclables,2200,kg,Recycling,1,2025,Measured,Paper and plastic",
        "water": "building_code,source,usage_type,quantity,unit,month,year,data_quality,notes\nENG-01,Municipal,Domestic,1200,kL,1,2025,Meter reading,Main water supply\nENG-01,Borewell,Irrigation,800,kL,1,2025,Meter reading,Landscape pumping",
        "transport": "mode,fuel_type,distance_km,fuel_quantity,fuel_unit,passengers,frequency,charging_kwh,month,year,notes\nCampus Bus #01,Diesel,12000,3600,Liters,52,Daily,0,1,2025,Bus route 1\nCampus EV Buggy,Electricity,1200,0,Liters,8,Daily,400,1,2025,Internal EV shuttle"
    }
    return templates.get(module_type, "building_code,quantity,unit,month,year\nENG-01,100,kWh,1,2025")

def import_activity_csv(db: Session, assessment_id: int, campus_id: int, module_type: str, csv_content: str) -> Dict[str, Any]:
    f = StringIO(csv_content.strip())
    reader = csv.DictReader(f)
    
    buildings = db.query(Building).filter(Building.campus_id == campus_id).all()
    bld_map = {b.building_code: b.id for b in buildings if b.building_code}
    bld_name_map = {b.name.lower(): b.id for b in buildings}

    imported_count = 0
    errors = []

    for row_idx, row in enumerate(reader, start=2):
        try:
            bld_code = row.get("building_code", "").strip()
            bld_id = bld_map.get(bld_code) or bld_name_map.get(bld_code.lower())

            qty = float(row.get("quantity", 0))
            if qty < 0:
                errors.append(f"Row {row_idx}: Quantity cannot be negative ({qty})")
                continue

            unit = row.get("unit", "kWh").strip()
            month = int(row.get("month", 1)) if row.get("month") else None
            year = int(row.get("year", 2025))
            data_quality = row.get("data_quality", "User entered").strip()
            notes = row.get("notes", "").strip()

            if module_type == "energy":
                energy_type = row.get("energy_type", "Grid Electricity").strip()
                source = row.get("source", "State Grid").strip()
                rec = EnergyRecord(
                    assessment_id=assessment_id,
                    campus_id=campus_id,
                    building_id=bld_id,
                    energy_type=energy_type,
                    source=source,
                    quantity=qty,
                    unit=unit,
                    month=month,
                    year=year,
                    data_quality=data_quality,
                    notes=notes
                )
                db.add(rec)
                imported_count += 1

            elif module_type == "waste":
                waste_type = row.get("waste_type", "General waste").strip()
                disposal = row.get("disposal_method", "Composting").strip()
                rec = WasteRecord(
                    assessment_id=assessment_id,
                    campus_id=campus_id,
                    building_id=bld_id,
                    waste_type=waste_type,
                    quantity=qty,
                    unit=unit,
                    disposal_method=disposal,
                    month=month,
                    year=year,
                    data_quality=data_quality,
                    notes=notes
                )
                db.add(rec)
                imported_count += 1

            elif module_type == "water":
                source = row.get("source", "Municipal").strip()
                usage_type = row.get("usage_type", "Domestic").strip()
                rec = WaterRecord(
                    assessment_id=assessment_id,
                    campus_id=campus_id,
                    building_id=bld_id,
                    source=source,
                    usage_type=usage_type,
                    quantity=qty,
                    unit=unit,
                    month=month,
                    year=year,
                    data_quality=data_quality,
                    notes=notes
                )
                db.add(rec)
                imported_count += 1

        except Exception as e:
            errors.append(f"Row {row_idx}: {str(e)}")

    db.commit()
    return {
        "success": len(errors) == 0,
        "imported_count": imported_count,
        "errors": errors
    }
