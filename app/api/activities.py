from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.activity import (
    EnergyRecord, RenewableRecord, TransportRecord, WasteRecord,
    WaterRecord, WastewaterRecord, GreenRecord, FoodRecord, IndustrialRecord,
    WaterConservationRecord, WaterBodyRecord, AnimalRecord
)
from app.schemas.schemas import (
    EnergyRecordCreate, EnergyRecordOut,
    RenewableRecordCreate, RenewableRecordOut,
    TransportRecordCreate, TransportRecordOut,
    WasteRecordCreate, WasteRecordOut,
    WaterRecordCreate, WaterRecordOut,
    WastewaterRecordCreate, WastewaterRecordOut,
    GreenRecordCreate, GreenRecordOut,
    FoodRecordCreate, FoodRecordOut,
    IndustrialRecordCreate, IndustrialRecordOut,
    WaterConservationRecordCreate, WaterConservationRecordOut,
    WaterBodyRecordCreate, WaterBodyRecordOut,
    AnimalRecordCreate, AnimalRecordOut
)
from app.models.assessment import Assessment

router = APIRouter(prefix="/api/activities", tags=["Activity Data Streams"])

# Helper to get campus_id from assessment
def get_assessment_campus(db: Session, assessment_id: int):
    asm = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not asm:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return asm.campus_id

# 1. Energy & Electricity
@router.get("/energy", response_model=list[EnergyRecordOut])
def list_energy(assessment_id: int, db: Session = Depends(get_db)):
    return db.query(EnergyRecord).filter(EnergyRecord.assessment_id == assessment_id).all()

@router.post("/energy", response_model=EnergyRecordOut)
def create_energy(assessment_id: int, rec_in: EnergyRecordCreate, db: Session = Depends(get_db)):
    campus_id = get_assessment_campus(db, assessment_id)
    rec = EnergyRecord(**rec_in.dict(), assessment_id=assessment_id, campus_id=campus_id)
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec

@router.delete("/energy/{record_id}")
def delete_energy(record_id: int, db: Session = Depends(get_db)):
    rec = db.query(EnergyRecord).filter(EnergyRecord.id == record_id).first()
    if rec:
        db.delete(rec)
        db.commit()
    return {"success": True}

# 2. Solar & Renewables
@router.get("/renewables", response_model=list[RenewableRecordOut])
def list_renewables(assessment_id: int, db: Session = Depends(get_db)):
    return db.query(RenewableRecord).filter(RenewableRecord.assessment_id == assessment_id).all()

@router.post("/renewables", response_model=RenewableRecordOut)
def create_renewable(assessment_id: int, rec_in: RenewableRecordCreate, db: Session = Depends(get_db)):
    campus_id = get_assessment_campus(db, assessment_id)
    rec = RenewableRecord(**rec_in.dict(), assessment_id=assessment_id, campus_id=campus_id)
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec

@router.delete("/renewables/{record_id}")
def delete_renewable(record_id: int, db: Session = Depends(get_db)):
    rec = db.query(RenewableRecord).filter(RenewableRecord.id == record_id).first()
    if rec:
        db.delete(rec)
        db.commit()
    return {"success": True}

# 3. Transport & Fleet
@router.get("/transport", response_model=list[TransportRecordOut])
def list_transport(assessment_id: int, db: Session = Depends(get_db)):
    return db.query(TransportRecord).filter(TransportRecord.assessment_id == assessment_id).all()

@router.post("/transport", response_model=TransportRecordOut)
def create_transport(assessment_id: int, rec_in: TransportRecordCreate, db: Session = Depends(get_db)):
    campus_id = get_assessment_campus(db, assessment_id)
    rec = TransportRecord(**rec_in.dict(), assessment_id=assessment_id, campus_id=campus_id)
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec

@router.delete("/transport/{record_id}")
def delete_transport(record_id: int, db: Session = Depends(get_db)):
    rec = db.query(TransportRecord).filter(TransportRecord.id == record_id).first()
    if rec:
        db.delete(rec)
        db.commit()
    return {"success": True}

# 4. Waste
@router.get("/waste", response_model=list[WasteRecordOut])
def list_waste(assessment_id: int, db: Session = Depends(get_db)):
    return db.query(WasteRecord).filter(WasteRecord.assessment_id == assessment_id).all()

@router.post("/waste", response_model=WasteRecordOut)
def create_waste(assessment_id: int, rec_in: WasteRecordCreate, db: Session = Depends(get_db)):
    campus_id = get_assessment_campus(db, assessment_id)
    rec = WasteRecord(**rec_in.dict(), assessment_id=assessment_id, campus_id=campus_id)
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec

@router.delete("/waste/{record_id}")
def delete_waste(record_id: int, db: Session = Depends(get_db)):
    rec = db.query(WasteRecord).filter(WasteRecord.id == record_id).first()
    if rec:
        db.delete(rec)
        db.commit()
    return {"success": True}

# 5. Water
@router.get("/water", response_model=list[WaterRecordOut])
def list_water(assessment_id: int, db: Session = Depends(get_db)):
    return db.query(WaterRecord).filter(WaterRecord.assessment_id == assessment_id).all()

@router.post("/water", response_model=WaterRecordOut)
def create_water(assessment_id: int, rec_in: WaterRecordCreate, db: Session = Depends(get_db)):
    campus_id = get_assessment_campus(db, assessment_id)
    rec = WaterRecord(**rec_in.dict(), assessment_id=assessment_id, campus_id=campus_id)
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec

@router.delete("/water/{record_id}")
def delete_water(record_id: int, db: Session = Depends(get_db)):
    rec = db.query(WaterRecord).filter(WaterRecord.id == record_id).first()
    if rec:
        db.delete(rec)
        db.commit()
    return {"success": True}

# 6. Wastewater
@router.get("/wastewater", response_model=list[WastewaterRecordOut])
def list_wastewater(assessment_id: int, db: Session = Depends(get_db)):
    return db.query(WastewaterRecord).filter(WastewaterRecord.assessment_id == assessment_id).all()

@router.post("/wastewater", response_model=WastewaterRecordOut)
def create_wastewater(assessment_id: int, rec_in: WastewaterRecordCreate, db: Session = Depends(get_db)):
    campus_id = get_assessment_campus(db, assessment_id)
    rec = WastewaterRecord(**rec_in.dict(), assessment_id=assessment_id, campus_id=campus_id)
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec

@router.delete("/wastewater/{record_id}")
def delete_wastewater(record_id: int, db: Session = Depends(get_db)):
    rec = db.query(WastewaterRecord).filter(WastewaterRecord.id == record_id).first()
    if rec:
        db.delete(rec)
        db.commit()
    return {"success": True}

# 7. Greenery / Trees
@router.get("/green", response_model=list[GreenRecordOut])
def list_green(assessment_id: int, db: Session = Depends(get_db)):
    return db.query(GreenRecord).filter(GreenRecord.assessment_id == assessment_id).all()

@router.post("/green", response_model=GreenRecordOut)
def create_green(assessment_id: int, rec_in: GreenRecordCreate, db: Session = Depends(get_db)):
    campus_id = get_assessment_campus(db, assessment_id)
    rec = GreenRecord(**rec_in.dict(), assessment_id=assessment_id, campus_id=campus_id)
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec

@router.delete("/green/{record_id}")
def delete_green(record_id: int, db: Session = Depends(get_db)):
    rec = db.query(GreenRecord).filter(GreenRecord.id == record_id).first()
    if rec:
        db.delete(rec)
        db.commit()
    return {"success": True}

# 8. Water Conservation
@router.get("/water-conservation", response_model=list[WaterConservationRecordOut])
def list_water_conservation(assessment_id: int, db: Session = Depends(get_db)):
    return db.query(WaterConservationRecord).filter(WaterConservationRecord.assessment_id == assessment_id).all()

@router.post("/water-conservation", response_model=WaterConservationRecordOut)
def create_water_conservation(assessment_id: int, rec_in: WaterConservationRecordCreate, db: Session = Depends(get_db)):
    campus_id = get_assessment_campus(db, assessment_id)
    rec = WaterConservationRecord(**rec_in.dict(), assessment_id=assessment_id, campus_id=campus_id)
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec

@router.delete("/water-conservation/{record_id}")
def delete_water_conservation(record_id: int, db: Session = Depends(get_db)):
    rec = db.query(WaterConservationRecord).filter(WaterConservationRecord.id == record_id).first()
    if rec:
        db.delete(rec)
        db.commit()
    return {"success": True}

# 9. Water Bodies
@router.get("/water-bodies", response_model=list[WaterBodyRecordOut])
def list_water_bodies(assessment_id: int, db: Session = Depends(get_db)):
    return db.query(WaterBodyRecord).filter(WaterBodyRecord.assessment_id == assessment_id).all()

@router.post("/water-bodies", response_model=WaterBodyRecordOut)
def create_water_body(assessment_id: int, rec_in: WaterBodyRecordCreate, db: Session = Depends(get_db)):
    campus_id = get_assessment_campus(db, assessment_id)
    rec = WaterBodyRecord(**rec_in.dict(), assessment_id=assessment_id, campus_id=campus_id)
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec

@router.delete("/water-bodies/{record_id}")
def delete_water_body(record_id: int, db: Session = Depends(get_db)):
    rec = db.query(WaterBodyRecord).filter(WaterBodyRecord.id == record_id).first()
    if rec:
        db.delete(rec)
        db.commit()
    return {"success": True}

# 10. Animals
@router.get("/animals", response_model=list[AnimalRecordOut])
def list_animals(assessment_id: int, db: Session = Depends(get_db)):
    return db.query(AnimalRecord).filter(AnimalRecord.assessment_id == assessment_id).all()

@router.post("/animals", response_model=AnimalRecordOut)
def create_animal(assessment_id: int, rec_in: AnimalRecordCreate, db: Session = Depends(get_db)):
    campus_id = get_assessment_campus(db, assessment_id)
    rec = AnimalRecord(**rec_in.dict(), assessment_id=assessment_id, campus_id=campus_id)
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec

@router.delete("/animals/{record_id}")
def delete_animal(record_id: int, db: Session = Depends(get_db)):
    rec = db.query(AnimalRecord).filter(AnimalRecord.id == record_id).first()
    if rec:
        db.delete(rec)
        db.commit()
    return {"success": True}

# 11. Food / Canteens
@router.get("/food", response_model=list[FoodRecordOut])
def list_food(assessment_id: int, db: Session = Depends(get_db)):
    return db.query(FoodRecord).filter(FoodRecord.assessment_id == assessment_id).all()

@router.post("/food", response_model=FoodRecordOut)
def create_food(assessment_id: int, rec_in: FoodRecordCreate, db: Session = Depends(get_db)):
    campus_id = get_assessment_campus(db, assessment_id)
    rec = FoodRecord(**rec_in.dict(), assessment_id=assessment_id, campus_id=campus_id)
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec

@router.delete("/food/{record_id}")
def delete_food(record_id: int, db: Session = Depends(get_db)):
    rec = db.query(FoodRecord).filter(FoodRecord.id == record_id).first()
    if rec:
        db.delete(rec)
        db.commit()
    return {"success": True}

# 12. Industrial
@router.get("/industrial", response_model=list[IndustrialRecordOut])
def list_industrial(assessment_id: int, db: Session = Depends(get_db)):
    return db.query(IndustrialRecord).filter(IndustrialRecord.assessment_id == assessment_id).all()

@router.post("/industrial", response_model=IndustrialRecordOut)
def create_industrial(assessment_id: int, rec_in: IndustrialRecordCreate, db: Session = Depends(get_db)):
    campus_id = get_assessment_campus(db, assessment_id)
    rec = IndustrialRecord(**rec_in.dict(), assessment_id=assessment_id, campus_id=campus_id)
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec

@router.delete("/industrial/{record_id}")
def delete_industrial(record_id: int, db: Session = Depends(get_db)):
    rec = db.query(IndustrialRecord).filter(IndustrialRecord.id == record_id).first()
    if rec:
        db.delete(rec)
        db.commit()
    return {"success": True}
