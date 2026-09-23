import uvicorn
import os
import sys

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

if __name__ == "__main__":
    print("==================================================================")
    print("  CAMPUS CARBON (Version 2.0) — Server Initializing")
    print("  Universal Campus Carbon Footprint Assessment & Management Platform")
    print("==================================================================")
    print("  Dashboard UI: http://127.0.0.1:8000")
    print("  Interactive API Docs (Swagger): http://127.0.0.1:8000/docs")
    print("  ReDoc: http://127.0.0.1:8000/redoc")
    print("==================================================================")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
