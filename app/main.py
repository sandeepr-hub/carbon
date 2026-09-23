import os
from fastapi import FastAPI, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.config import APP_TITLE, APP_SUBTITLE, APP_VERSION, STATIC_DIR, TEMPLATES_DIR
from app.database import engine, Base, get_db
from app.seed.factors_seed import seed_emission_factors
from app.seed.demo_data import seed_demo_data
from app.seed.more_campuses import seed_additional_campuses
from app.engine.carbon_calculator import calculate_gross_emissions
from app.engine.reduction_calculator import calculate_reduction_contributions
from app.engine.aggregator import aggregate_assessment_summary

from app.api.auth import router as auth_router
from app.api.campuses import router as campuses_router
from app.api.assessments import router as assessments_router
from app.api.activities import router as activities_router
from app.api.carbon import router as carbon_router
from app.api.emission_factors import router as factors_router
from app.api.scenarios import router as scenarios_router
from app.api.recommendations import router as recommendations_router
from app.api.benchmarks import router as benchmarks_router
from app.api.reports import router as reports_router
from app.api.import_export import router as import_export_router

import app.models

# Create all database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=APP_TITLE,
    description=f"{APP_SUBTITLE} (Version {APP_VERSION})",
    version=APP_VERSION
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static & Templates
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Include API Routers
app.include_router(auth_router)
app.include_router(campuses_router)
app.include_router(assessments_router)
app.include_router(activities_router)
app.include_router(carbon_router)
app.include_router(factors_router)
app.include_router(scenarios_router)
app.include_router(recommendations_router)
app.include_router(benchmarks_router)
app.include_router(reports_router)
app.include_router(import_export_router)

@app.on_event("startup")
def startup_event():
    db = next(get_db())
    try:
        seed_emission_factors(db)
        seed_demo_data(db)
        seed_additional_campuses(db)
        # Calculate summary for demo assessment 1
        calculate_gross_emissions(db, 1)
        calculate_reduction_contributions(db, 1)
        aggregate_assessment_summary(db, 1)
        print("Campus Carbon initialized and seeded successfully.")
    finally:
        db.close()

@app.get("/")
def serve_home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "app_title": APP_TITLE,
            "app_subtitle": APP_SUBTITLE,
            "app_version": APP_VERSION
        }
    )

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "app": APP_TITLE,
        "version": APP_VERSION
    }
