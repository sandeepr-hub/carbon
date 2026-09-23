# CAMPUS CARBON (Version 2.0)
## Universal Campus Carbon Footprint Assessment & Management Platform
### Positive, Negative & Net Carbon Accounting Architecture

---

## 1. Overview & Vision
**CAMPUS CARBON** is an enterprise-grade, configuration-driven greenhouse gas (GHG) accounting and sustainability intelligence platform. Built in strict accordance with the **GHG Protocol Corporate Standard** and **ISO 14064-1:2018**, the platform assesses, tracks, manages, simulates, and reports emissions across diverse campus types:
- **Universities & Colleges** (e.g. Christ University – Kengeri Campus profile: 78.5 acres, 13 buildings, 6450 occupants, solar PV, STP, canteens, native tree canopy)
- **Schools** (e.g. Greenwood International School)
- **Apartment Societies & Gated Communities** (e.g. Palm Meadows Residential Society)
- **Hospitals & Healthcare Campuses** (e.g. Apex Multi-Specialty Hospital)
- **Industrial Plants & Manufacturing Hubs** (e.g. Precision Heavy Engineering Plant)
- **Corporate & IT Office Parks** (e.g. TechnoPark Corporate Hub)
- **Government & Institutional Facilities**
- **Custom Campus Configurations**

---

## 2. Fundamental Carbon Accounting Model (3 Pillars)

```
+------------------------------------+
|  1. GROSS / POSITIVE EMISSIONS     |  --> Scope 1 (Direct fuel, fleet, process)
|     XXXX.XX tCO2e                  |  --> Scope 2 (Purchased grid electricity)
+------------------------------------+  --> Scope 3 (Commuting, waste, water, STP)
                 |
                 v
+------------------------------------+
|  2. ELIGIBLE REDUCTIONS & REMOVALS |  --> Tree biomass carbon sequestration
|     -XXX.XX tCO2e                  |  --> Avoided EV transport emissions vs ICE baseline
+------------------------------------+  --> Avoided landfill methane via composting/recycling
                 |
                 v
+------------------------------------+
|  3. NET CARBON FOOTPRINT           |  --> Net = Gross Emissions − Eligible Reductions
|     XXXX.XX tCO2e                  |  --> Transparent side-by-side auditability
+------------------------------------+
```

### Anti-Double-Counting Safeguards:
1. **Solar Self-Consumption**: On-site solar electricity directly replaces purchased grid electricity, lowering Scope 2 gross emissions. It is **not** subtracted a second time as a negative offset.
2. **EV Fleet Transition**: EV charging electricity is accounted for under Scope 2 electricity. Avoided transport reductions are calculated strictly as $(\text{Baseline ICE Fuel Emissions} - \text{EV Electricity Emissions})$.
3. **Non-Negative Activity Data**: Ordinary activity fields reject negative values; all reductions are recorded in the dedicated `carbon_reduction_contributions` ledger.

---

## 3. Platform Capabilities & Modules

1. **Executive Dashboard**:
   - 3-Pillar Hero Scorecards (Gross, Reductions, Net).
   - Scope 1, Scope 2, Scope 3 breakdown cards.
   - Intensity Indicators: $\text{tCO}_2\text{e}/\text{person}$, $\text{tCO}_2\text{e}/\text{m}^2$, Renewable Energy %, Waste Diversion Rate %.
   - Interactive Gross $\rightarrow$ Reductions $\rightarrow$ Net Waterfall Visualizer & Scope Donut.

2. **Dynamic Campus & Building Configurator**:
   - Multi-building floor plans, occupancy categories, operating hours, and geometry.
   - Dynamic module activation based on campus type.

3. **Activity Data Entry Studio**:
   - Energy & Fuels (Grid electricity, DG diesel, LPG, Natural gas, Petrol, Biomass).
   - Solar & Renewables (Solar PV, Wind, Biogas, on-site vs exported power).
   - Transport & Mobility (Fleet inventory, Commuting surveys, EV charging hubs).
   - Solid Waste Streams (Food, Organic, Paper, Plastic, E-waste, Biomedical, Landfill vs Composting vs Recycling).
   - Water & Wastewater (Borewell, Municipal, Rainwater, SBR Central STP, Recycled water reuse).
   - Greenery & Sequestration (Green cover area, mature tree census, annual biomass absorption).
   - Canteens & Kitchens (Meals served, cooking LPG, food waste).
   - Industrial Processes (Production tonnage, process mass balance emissions, refrigerants GWP100).

4. **Carbon Accounting Audit Log**:
   - Atomic calculation trace of every activity-to-emission step with emission factor source and citation.
   - Negative / Removal Contributions Ledger with baseline definitions and eligibility status.

5. **Building-wise Analytics**:
   - Ranked leaderboard by total emissions, per-person intensity, and $\text{kgCO}_2\text{e}/\text{m}^2$.

6. **Graphical Insights**:
   - Monthly time-series trajectory and building-by-building gross vs net comparison.

7. **Interactive What-If Scenario Simulator**:
   - Live sliders for Energy Efficiency %, Solar Capacity (+kWp), EV Fleet Transition %, Waste Diversion %, Water Conservation %, and Additional Tree Plantation.
   - Real-time delta and % reduction preview without mutating base database records.
   - Save named simulation cases.

8. **AI / Rule-Based Recommendations**:
   - Hotspot identification and prioritized intervention roadmap (High/Medium/Low priority, estimated % impact, direct scenario links).

9. **Cross-Campus & Historical Benchmarking**:
   - Normalized multi-campus comparison across archetypes.

10. **Emission Factors Reference Library**:
    - Comprehensive pre-seeded library (CEA India v19, IPCC AR5/AR6, DEFRA 2024, US EPA eGRID) with search, filtering, and custom factor support.

11. **Professional Report Studio**:
    - **Executive PDF Report (ReportLab)**: 15+ section complete audit report.
    - **Multi-Tab Excel Workbook (openpyxl)**: Formatted worksheets (Summary, Buildings, Gross Calculations, Reductions Ledger, Factors).
    - **Tabular CSV Export**.

12. **Data Import / Export**:
    - Pre-formatted CSV templates and bulk CSV upload with automated validation.

---

## 4. Technology Stack
- **Backend**: Python 3.10, FastAPI 0.141, Uvicorn 0.52, SQLAlchemy 2.0, SQLite3, Pydantic v2
- **Engines**: Custom Carbon Engine, Reduction Engine, Aggregator, What-If Simulator, ReportLab (PDF), openpyxl (Excel), pandas
- **Frontend**: Tailwind CSS, Chart.js, Lucide Icons, Vanilla JavaScript SPA

---

## 5. How to Run the Platform

```bash
# 1. Navigate to project directory
cd "C:\Users\Sandeep Rajendran\.gemini\antigravity\scratch\campus_carbon"

# 2. Run the application server
python run_server.py

# 3. Open your browser
# Dashboard: http://127.0.0.1:8000
# API Docs:  http://127.0.0.1:8000/docs
```

---

## 6. Verification & Automated Tests
To run the automated verification test suite:
```bash
python "C:\Users\Sandeep Rajendran\.gemini\antigravity\brain\a08bdea3-063d-46d8-8ef7-c96a49a2aeed\scratch\run_tests.py"
python "C:\Users\Sandeep Rajendran\.geminintigravity\brain\a08bdea3-063d-46d8-8ef7-c96a49a2aeed\scratch\test_api_runner.py"
```
