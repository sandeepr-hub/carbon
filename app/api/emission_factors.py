from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.carbon import EmissionFactor
from app.schemas.schemas import EmissionFactorCreate, EmissionFactorOut

router = APIRouter(prefix="/api/factors", tags=["Emission Factors Database"])

@router.get("/", response_model=list[EmissionFactorOut])
def list_factors(category: str = None, scope: str = None, db: Session = Depends(get_db)):
    query = db.query(EmissionFactor)
    if category:
        query = query.filter(EmissionFactor.category == category)
    if scope:
        query = query.filter(EmissionFactor.scope == scope)
    return query.all()

@router.post("/", response_model=EmissionFactorOut)
def create_factor(ef_in: EmissionFactorCreate, db: Session = Depends(get_db)):
    ef = EmissionFactor(**ef_in.dict())
    db.add(ef)
    db.commit()
    db.refresh(ef)
    return ef
