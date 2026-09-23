import os
from pathlib import Path

BASE_DIR = Path(r"C:\Users\Sandeep Rajendran\.gemini\antigravity\scratch\campus_carbon").resolve()
DATA_DIR = BASE_DIR / "data"
EXPORT_DIR = BASE_DIR / "exports"
STATIC_DIR = BASE_DIR / "app" / "static"
TEMPLATES_DIR = BASE_DIR / "app" / "templates"

DATA_DIR.mkdir(parents=True, exist_ok=True)
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_URL = f"sqlite:///{DATA_DIR / 'campus_carbon.db'}"

APP_TITLE = "CAMPUS CARBON"
APP_SUBTITLE = "Universal Campus Carbon Footprint Assessment and Management Platform"
APP_VERSION = "2.0.0"
SECRET_KEY = "campus-carbon-enterprise-secret-v2"
