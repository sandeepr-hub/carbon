from app.models.carbon import EmissionFactor

DEFAULT_EMISSION_FACTORS = [
    # Scope 2 - Electricity
    {
        "category": "Electricity",
        "activity": "Grid Electricity (India National Grid Average)",
        "fuel_type": "Grid Mix",
        "unit": "kWh",
        "factor": 0.716, # kg CO2e / kWh
        "factor_unit": "kgCO2e/kWh",
        "scope": "Scope 2",
        "source": "CEA India CO2 Baseline Database v19 (2024)",
        "reference_year": 2024,
        "region": "India",
        "notes": "User-end weighted average grid emission factor for Indian National Grid.",
        "is_custom": False
    },
    {
        "category": "Electricity",
        "activity": "Grid Electricity (US eGRID Average)",
        "fuel_type": "Grid Mix",
        "unit": "kWh",
        "factor": 0.386,
        "factor_unit": "kgCO2e/kWh",
        "scope": "Scope 2",
        "source": "US EPA eGRID (2024)",
        "reference_year": 2024,
        "region": "US",
        "notes": "US national average electricity emission factor.",
        "is_custom": False
    },
    {
        "category": "Electricity",
        "activity": "Grid Electricity (UK Grid Average)",
        "fuel_type": "Grid Mix",
        "unit": "kWh",
        "factor": 0.207,
        "factor_unit": "kgCO2e/kWh",
        "scope": "Scope 2",
        "source": "UK DESNZ / DEFRA (2024)",
        "reference_year": 2024,
        "region": "UK",
        "notes": "UK national transmission & distribution grid average.",
        "is_custom": False
    },

    # Scope 1 - Stationary Combustion
    {
        "category": "Stationary Fuel",
        "activity": "Diesel Fuel Combustion (DG Sets / Boilers)",
        "fuel_type": "Diesel",
        "unit": "Liters",
        "factor": 2.687, # kg CO2e / Liter
        "factor_unit": "kgCO2e/Liter",
        "scope": "Scope 1",
        "source": "IPCC Guidelines for National GHG Inventories / DEFRA 2024",
        "reference_year": 2024,
        "region": "Global",
        "notes": "Stationary diesel generator and thermal combustion emission factor.",
        "is_custom": False
    },
    {
        "category": "Stationary Fuel",
        "activity": "LPG Combustion (Kitchens / Laboratories)",
        "fuel_type": "LPG",
        "unit": "kg",
        "factor": 2.983, # kg CO2e / kg
        "factor_unit": "kgCO2e/kg",
        "scope": "Scope 1",
        "source": "IPCC 2006 / DEFRA 2024",
        "reference_year": 2024,
        "region": "Global",
        "notes": "Liquefied Petroleum Gas combustion for cooking and lab heating.",
        "is_custom": False
    },
    {
        "category": "Stationary Fuel",
        "activity": "Natural Gas Combustion",
        "fuel_type": "Natural Gas",
        "unit": "m3",
        "factor": 1.984,
        "factor_unit": "kgCO2e/m3",
        "scope": "Scope 1",
        "source": "IPCC 2006 Guidelines / DEFRA 2024",
        "reference_year": 2024,
        "region": "Global",
        "notes": "Piped Natural Gas (PNG) / standard cubic meter.",
        "is_custom": False
    },
    {
        "category": "Stationary Fuel",
        "activity": "Biomass / Firewood Combustion",
        "fuel_type": "Biomass",
        "unit": "kg",
        "factor": 0.018, # Non-CO2 CH4 and N2O lifecycle
        "factor_unit": "kgCO2e/kg",
        "scope": "Scope 1",
        "source": "IPCC 2006 (CH4 & N2O only; biogenic CO2 reported separately)",
        "reference_year": 2024,
        "region": "Global",
        "notes": "Biogenic fuel with non-CO2 combustion emissions.",
        "is_custom": False
    },

    # Scope 1 - Mobile Combustion (Campus-owned Fleet)
    {
        "category": "Mobile Fuel",
        "activity": "Diesel Vehicle Fleet (Buses, Ambulances, Tractors, Trucks)",
        "fuel_type": "Diesel",
        "unit": "Liters",
        "factor": 2.687,
        "factor_unit": "kgCO2e/Liter",
        "scope": "Scope 1",
        "source": "DEFRA 2024 / IPCC",
        "reference_year": 2024,
        "region": "Global",
        "notes": "Direct tailpipe emissions from campus-owned diesel vehicles.",
        "is_custom": False
    },
    {
        "category": "Mobile Fuel",
        "activity": "Petrol Vehicle Fleet (Cars, Two-wheelers)",
        "fuel_type": "Petrol",
        "unit": "Liters",
        "factor": 2.314,
        "factor_unit": "kgCO2e/Liter",
        "scope": "Scope 1",
        "source": "DEFRA 2024 / IPCC",
        "reference_year": 2024,
        "region": "Global",
        "notes": "Direct tailpipe emissions from campus-owned petrol vehicles.",
        "is_custom": False
    },
    {
        "category": "Mobile Fuel",
        "activity": "CNG Fleet Vehicles",
        "fuel_type": "CNG",
        "unit": "kg",
        "factor": 2.748,
        "factor_unit": "kgCO2e/kg",
        "scope": "Scope 1",
        "source": "DEFRA 2024 / ARAI India",
        "reference_year": 2024,
        "region": "India",
        "notes": "Compressed Natural Gas vehicular tailpipe emission.",
        "is_custom": False
    },

    # Scope 1 - Refrigerants & Fugitive Losses
    {
        "category": "Refrigerant",
        "activity": "Refrigerant Loss - R-410A (HVAC / VRF Systems)",
        "fuel_type": "R-410A",
        "unit": "kg",
        "factor": 2088.0,
        "factor_unit": "kgCO2e/kg",
        "scope": "Scope 1",
        "source": "IPCC AR5 / Montreal Protocol",
        "reference_year": 2024,
        "region": "Global",
        "notes": "Global Warming Potential (GWP100) of R-410A refrigerant gas.",
        "is_custom": False
    },
    {
        "category": "Refrigerant",
        "activity": "Refrigerant Loss - R-134a (Chillers / Automotive AC)",
        "fuel_type": "R-134a",
        "unit": "kg",
        "factor": 1430.0,
        "factor_unit": "kgCO2e/kg",
        "scope": "Scope 1",
        "source": "IPCC AR5",
        "reference_year": 2024,
        "region": "Global",
        "notes": "GWP100 of R-134a refrigerant.",
        "is_custom": False
    },
    {
        "category": "Refrigerant",
        "activity": "Refrigerant Loss - R-32 (Next-gen Split ACs)",
        "fuel_type": "R-32",
        "unit": "kg",
        "factor": 675.0,
        "factor_unit": "kgCO2e/kg",
        "scope": "Scope 1",
        "source": "IPCC AR5",
        "reference_year": 2024,
        "region": "Global",
        "notes": "GWP100 of R-32 refrigerant.",
        "is_custom": False
    },

    # Scope 3 - Waste Disposal
    {
        "category": "Waste",
        "activity": "General Municipal Solid Waste to Landfill",
        "fuel_type": "Municipal Waste",
        "unit": "kg",
        "factor": 0.450,
        "factor_unit": "kgCO2e/kg",
        "scope": "Scope 3",
        "source": "IPCC Waste Model / DEFRA 2024",
        "reference_year": 2024,
        "region": "Global",
        "notes": "Methane generation from mixed municipal waste decomposition in landfill.",
        "is_custom": False
    },
    {
        "category": "Waste",
        "activity": "Food & Organic Waste to Landfill (Unmanaged)",
        "fuel_type": "Organic Waste",
        "unit": "kg",
        "factor": 0.580,
        "factor_unit": "kgCO2e/kg",
        "scope": "Scope 3",
        "source": "IPCC 2006 Waste Model",
        "reference_year": 2024,
        "region": "Global",
        "notes": "High methane yield from organic waste anaerobic decomposition in dumpsite.",
        "is_custom": False
    },
    {
        "category": "Waste",
        "activity": "Organic Waste Composting (Managed Aerobic)",
        "fuel_type": "Organic Waste",
        "unit": "kg",
        "factor": 0.010,
        "factor_unit": "kgCO2e/kg",
        "scope": "Scope 3",
        "source": "DEFRA 2024 / IPCC",
        "reference_year": 2024,
        "region": "Global",
        "notes": "Minimal non-CO2 process emissions from aerobic windrow/drum composting.",
        "is_custom": False
    },
    {
        "category": "Waste",
        "activity": "Dry Waste Recycling (Paper, Plastic, Metal, Glass)",
        "fuel_type": "Recyclables",
        "unit": "kg",
        "factor": 0.021,
        "factor_unit": "kgCO2e/kg",
        "scope": "Scope 3",
        "source": "DEFRA 2024 Material Fact Sheet",
        "reference_year": 2024,
        "region": "Global",
        "notes": "Logistics and handling emissions for closed-loop recycling.",
        "is_custom": False
    },
    {
        "category": "Waste",
        "activity": "Biomedical / Hazardous Waste Incineration",
        "fuel_type": "Hazardous Waste",
        "unit": "kg",
        "factor": 1.120,
        "factor_unit": "kgCO2e/kg",
        "scope": "Scope 3",
        "source": "CPCB Guidelines / DEFRA 2024",
        "reference_year": 2024,
        "region": "India",
        "notes": "High-temperature dual chamber incineration emission factor.",
        "is_custom": False
    },

    # Scope 3 - Water & Wastewater
    {
        "category": "Water",
        "activity": "Municipal Water Supply & Distribution",
        "fuel_type": "Freshwater",
        "unit": "kL",
        "factor": 0.344,
        "factor_unit": "kgCO2e/kL",
        "scope": "Scope 3",
        "source": "CPCB India / UK Water Industry Research",
        "reference_year": 2024,
        "region": "India",
        "notes": "Emissions from water treatment, booster pumping and pipeline distribution.",
        "is_custom": False
    },
    {
        "category": "Water",
        "activity": "Borewell Groundwater Pumping",
        "fuel_type": "Groundwater",
        "unit": "kL",
        "factor": 0.285,
        "factor_unit": "kgCO2e/kL",
        "scope": "Scope 3",
        "source": "BEE India Agricultural & Deep Well Pumping Benchmark",
        "reference_year": 2024,
        "region": "India",
        "notes": "Submersible pump energy footprint per kiloliter extracted.",
        "is_custom": False
    },
    {
        "category": "Water",
        "activity": "Wastewater Treatment (Central STP)",
        "fuel_type": "Sewage",
        "unit": "kL",
        "factor": 0.708,
        "factor_unit": "kgCO2e/kL",
        "scope": "Scope 3",
        "source": "DEFRA 2024 / CPCB Sewage Treatment Life Cycle",
        "reference_year": 2024,
        "region": "India",
        "notes": "Biological aeration, sludge handling, and effluent filtration.",
        "is_custom": False
    },

    # Scope 3 - Commuting & Student/Staff Transport
    {
        "category": "Transport",
        "activity": "Commuting - Diesel Public / Contract Bus",
        "fuel_type": "Diesel",
        "unit": "passenger-km",
        "factor": 0.089,
        "factor_unit": "kgCO2e/p-km",
        "scope": "Scope 3",
        "source": "ARAI India / DEFRA 2024",
        "reference_year": 2024,
        "region": "India",
        "notes": "Average occupancy commuter bus factor.",
        "is_custom": False
    },
    {
        "category": "Transport",
        "activity": "Commuting - Two-Wheeler (Motorcycle / Scooter)",
        "fuel_type": "Petrol",
        "unit": "passenger-km",
        "factor": 0.045,
        "factor_unit": "kgCO2e/p-km",
        "scope": "Scope 3",
        "source": "ARAI India (2024)",
        "reference_year": 2024,
        "region": "India",
        "notes": "Typical 125-150cc commuter motorcycle emission intensity.",
        "is_custom": False
    },
    {
        "category": "Transport",
        "activity": "Commuting - Personal Petrol Car (Single Occupancy)",
        "fuel_type": "Petrol",
        "unit": "passenger-km",
        "factor": 0.171,
        "fuel_type": "Petrol",
        "factor_unit": "kgCO2e/p-km",
        "scope": "Scope 3",
        "source": "DEFRA / BEE India (2024)",
        "reference_year": 2024,
        "region": "India",
        "notes": "Medium sedan/hatchback petrol car commuting factor.",
        "is_custom": False
    },
    {
        "category": "Transport",
        "activity": "Commuting - Metro Rail / Suburban Train",
        "fuel_type": "Electricity",
        "unit": "passenger-km",
        "factor": 0.028,
        "factor_unit": "kgCO2e/p-km",
        "scope": "Scope 3",
        "source": "DMRC / Namma Metro Energy Footprint",
        "reference_year": 2024,
        "region": "India",
        "notes": "Electric transit rail per passenger-kilometer.",
        "is_custom": False
    },

    # Sequestration Reference Factor
    {
        "category": "Sequestration",
        "activity": "Tree Carbon Sequestration (Mature Tropical / Subtropical)",
        "fuel_type": "Biomass Growth",
        "unit": "tree/year",
        "factor": 22.0, # kg CO2 absorbed per tree per year
        "factor_unit": "kgCO2/tree/year",
        "scope": "Scope 1",
        "source": "Forest Survey of India (FSI) & IPCC GPG for LULUCF",
        "reference_year": 2024,
        "region": "India",
        "notes": "Average annual biomass CO2 sequestration for semi-mature trees (e.g. Neem, Peepal, Teak, Rain tree).",
        "is_custom": False
    }
]

def seed_emission_factors(db):
    for ef_data in DEFAULT_EMISSION_FACTORS:
        existing = db.query(EmissionFactor).filter(
            EmissionFactor.activity == ef_data["activity"],
            EmissionFactor.category == ef_data["category"]
        ).first()
        if not existing:
            ef = EmissionFactor(**ef_data)
            db.add(ef)
    db.commit()
    print(f"Emission factors seeded successfully ({len(DEFAULT_EMISSION_FACTORS)} factors).")
