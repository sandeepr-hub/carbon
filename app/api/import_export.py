from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.engine.importer_exporter import generate_activity_csv_template, import_activity_csv

router = APIRouter(prefix="/api/exchange", tags=["Data Import & Export"])

@router.get("/template/{module_type}", response_class=PlainTextResponse)
def get_template(module_type: str):
    return generate_activity_csv_template(module_type)

@router.post("/import/{module_type}")
async def upload_csv(
    module_type: str,
    assessment_id: int = Form(...),
    campus_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    content = await file.read()
    csv_text = content.decode("utf-8")
    result = import_activity_csv(db, assessment_id, campus_id, module_type, csv_text)
    return result
