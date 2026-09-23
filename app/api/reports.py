from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.engine.report_generator import generate_pdf_report, generate_excel_report, generate_csv_report

router = APIRouter(prefix="/api/reports", tags=["Report Studio"])

@router.get("/pdf/{assessment_id}")
def download_pdf(assessment_id: int, db: Session = Depends(get_db)):
    file_path = generate_pdf_report(db, assessment_id)
    return FileResponse(file_path, media_type="application/pdf", filename=file_path.split("\\")[-1])

@router.get("/excel/{assessment_id}")
def download_excel(assessment_id: int, db: Session = Depends(get_db)):
    file_path = generate_excel_report(db, assessment_id)
    return FileResponse(file_path, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", filename=file_path.split("\\")[-1])

@router.get("/csv/{assessment_id}")
def download_csv(assessment_id: int, db: Session = Depends(get_db)):
    file_path = generate_csv_report(db, assessment_id)
    return FileResponse(file_path, media_type="text/csv", filename=file_path.split("\\")[-1])
