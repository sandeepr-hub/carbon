from sqlalchemy.orm import Session
from app.models.assessment import Assessment
from app.models.activity import (
    EnergyRecord, RenewableRecord, TransportRecord, WasteRecord,
    WaterRecord, WastewaterRecord, GreenRecord, FoodRecord, IndustrialRecord
)
from app.models.carbon import EmissionFactor, CarbonCalculation

def get_factor(db: Session, category: str, activity_keyword: str, fallback_factor: float, factor_unit: str, scope: str, source: str):
    ef = db.query(EmissionFactor).filter(
        EmissionFactor.category == category,
        EmissionFactor.activity.ilike(f"%{activity_keyword}%")
    ).first()
    if ef:
        return ef.factor, ef.factor_unit, ef.source, ef.scope
    return fallback_factor, factor_unit, source, scope

def calculate_gross_emissions(db: Session, assessment_id: int):
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        return []

    # Clear previous calculations for this assessment
    db.query(CarbonCalculation).filter(CarbonCalculation.assessment_id == assessment_id).delete()

    calculations = []

    # 1. Energy Records (Scope 1 & Scope 2)
    energy_records = db.query(EnergyRecord).filter(EnergyRecord.assessment_id == assessment_id).all()
    for rec in energy_records:
        if "Electricity" in rec.energy_type or "Grid" in rec.energy_type:
            factor, f_unit, f_src, scope = get_factor(db, "Electricity", "Grid", 0.716, "kgCO2e/kWh", "Scope 2", "CEA India v19")
            emissions = (rec.quantity * factor) / 1000.0 # tCO2e
            calc = CarbonCalculation(
                assessment_id=assessment_id,
                campus_id=rec.campus_id,
                building_id=rec.building_id,
                category="Electricity",
                activity=f"Grid Electricity ({rec.source})",
                scope="Scope 2",
                quantity=rec.quantity,
                unit=rec.unit,
                emission_factor=factor,
                emission_factor_unit=f_unit,
                emission_factor_source=f_src,
                emissions_co2e=round(emissions, 4),
                calculation_method="Quantity (kWh) x Grid EF / 1000",
                data_quality=rec.data_quality,
                month=rec.month,
                year=rec.year
            )
            calculations.append(calc)
        elif "Diesel" in rec.energy_type or "DG" in rec.energy_type:
            factor, f_unit, f_src, scope = get_factor(db, "Stationary Fuel", "Diesel", 2.687, "kgCO2e/Liter", "Scope 1", "IPCC / DEFRA")
            emissions = (rec.quantity * factor) / 1000.0
            calc = CarbonCalculation(
                assessment_id=assessment_id,
                campus_id=rec.campus_id,
                building_id=rec.building_id,
                category="Stationary Fuel",
                activity="Diesel Fuel for Backup DG Sets",
                scope="Scope 1",
                quantity=rec.quantity,
                unit=rec.unit,
                emission_factor=factor,
                emission_factor_unit=f_unit,
                emission_factor_source=f_src,
                emissions_co2e=round(emissions, 4),
                calculation_method="Quantity (Liters) x Diesel EF / 1000",
                data_quality=rec.data_quality,
                month=rec.month,
                year=rec.year
            )
            calculations.append(calc)
        elif "LPG" in rec.energy_type:
            factor, f_unit, f_src, scope = get_factor(db, "Stationary Fuel", "LPG", 2.983, "kgCO2e/kg", "Scope 1", "IPCC / DEFRA")
            emissions = (rec.quantity * factor) / 1000.0
            calc = CarbonCalculation(
                assessment_id=assessment_id,
                campus_id=rec.campus_id,
                building_id=rec.building_id,
                category="Stationary Fuel",
                activity="LPG Combustion (Kitchen / Labs)",
                scope="Scope 1",
                quantity=rec.quantity,
                unit=rec.unit,
                emission_factor=factor,
                emission_factor_unit=f_unit,
                emission_factor_source=f_src,
                emissions_co2e=round(emissions, 4),
                calculation_method="Quantity (kg) x LPG EF / 1000",
                data_quality=rec.data_quality,
                month=rec.month,
                year=rec.year
            )
            calculations.append(calc)
        elif "Natural Gas" in rec.energy_type:
            factor, f_unit, f_src, scope = get_factor(db, "Stationary Fuel", "Natural Gas", 1.984, "kgCO2e/m3", "Scope 1", "IPCC / DEFRA")
            emissions = (rec.quantity * factor) / 1000.0
            calc = CarbonCalculation(
                assessment_id=assessment_id,
                campus_id=rec.campus_id,
                building_id=rec.building_id,
                category="Stationary Fuel",
                activity="Natural Gas Piped Combustion",
                scope="Scope 1",
                quantity=rec.quantity,
                unit=rec.unit,
                emission_factor=factor,
                emission_factor_unit=f_unit,
                emission_factor_source=f_src,
                emissions_co2e=round(emissions, 4),
                calculation_method="Quantity (m3) x NG EF / 1000",
                data_quality=rec.data_quality,
                month=rec.month,
                year=rec.year
            )
            calculations.append(calc)

    # 2. Transport Records (Scope 1 Fleet, Scope 2 EV Charging, Scope 3 Commuting)
    transport_records = db.query(TransportRecord).filter(TransportRecord.assessment_id == assessment_id).all()
    for rec in transport_records:
        if rec.record_type == "Fleet":
            if rec.fuel_type == "Diesel" or "Diesel" in (rec.fuel_type or ""):
                factor, f_unit, f_src, scope = get_factor(db, "Mobile Fuel", "Diesel", 2.687, "kgCO2e/Liter", "Scope 1", "DEFRA / IPCC")
                qty = rec.fuel_quantity if rec.fuel_quantity > 0 else (rec.distance_km / 4.0 if rec.distance_km > 0 else 0)
                emissions = (qty * factor) / 1000.0
                calc = CarbonCalculation(
                    assessment_id=assessment_id,
                    campus_id=rec.campus_id,
                    building_id=rec.building_id,
                    category="Transport",
                    activity=f"Campus Fleet Diesel Combustion ({rec.mode or 'Fleet Vehicle'})",
                    scope="Scope 1",
                    quantity=qty,
                    unit="Liters",
                    emission_factor=factor,
                    emission_factor_unit=f_unit,
                    emission_factor_source=f_src,
                    emissions_co2e=round(emissions, 4),
                    calculation_method="Fuel Quantity (L) x Mobile Diesel EF / 1000",
                    data_quality=rec.data_quality,
                    month=rec.month,
                    year=rec.year
                )
                calculations.append(calc)
            elif rec.fuel_type == "Petrol":
                factor, f_unit, f_src, scope = get_factor(db, "Mobile Fuel", "Petrol", 2.314, "kgCO2e/Liter", "Scope 1", "DEFRA / IPCC")
                qty = rec.fuel_quantity if rec.fuel_quantity > 0 else (rec.distance_km / 12.0 if rec.distance_km > 0 else 0)
                emissions = (qty * factor) / 1000.0
                calc = CarbonCalculation(
                    assessment_id=assessment_id,
                    campus_id=rec.campus_id,
                    building_id=rec.building_id,
                    category="Transport",
                    activity=f"Campus Fleet Petrol Combustion ({rec.mode or 'Petrol Vehicle'})",
                    scope="Scope 1",
                    quantity=qty,
                    unit="Liters",
                    emission_factor=factor,
                    emission_factor_unit=f_unit,
                    emission_factor_source=f_src,
                    emissions_co2e=round(emissions, 4),
                    calculation_method="Fuel Quantity (L) x Petrol EF / 1000",
                    data_quality=rec.data_quality,
                    month=rec.month,
                    year=rec.year
                )
                calculations.append(calc)
        elif rec.record_type == "EV Charging":
            factor, f_unit, f_src, _ = get_factor(db, "Electricity", "Grid", 0.716, "kgCO2e/kWh", "Scope 2", "CEA India v19")
            emissions = (rec.charging_electricity_kwh * factor) / 1000.0
            calc = CarbonCalculation(
                assessment_id=assessment_id,
                campus_id=rec.campus_id,
                building_id=rec.building_id,
                category="Transport",
                activity=f"EV Operational Charging ({rec.mode or 'Campus EV'})",
                scope="Scope 2",
                quantity=rec.charging_electricity_kwh,
                unit="kWh",
                emission_factor=factor,
                emission_factor_unit=f_unit,
                emission_factor_source=f_src,
                emissions_co2e=round(emissions, 4),
                calculation_method="Charging Electricity (kWh) x Grid EF / 1000",
                data_quality=rec.data_quality,
                month=rec.month,
                year=rec.year
            )
            calculations.append(calc)
        elif rec.record_type == "Commuting":
            if "Two-Wheeler" in (rec.mode or ""):
                factor, f_unit, f_src, _ = get_factor(db, "Transport", "Two-Wheeler", 0.045, "kgCO2e/p-km", "Scope 3", "ARAI India")
            elif "Car" in (rec.mode or ""):
                factor, f_unit, f_src, _ = get_factor(db, "Transport", "Personal Petrol Car", 0.171, "kgCO2e/p-km", "Scope 3", "DEFRA / BEE")
            elif "Metro" in (rec.mode or "") or "Train" in (rec.mode or ""):
                factor, f_unit, f_src, _ = get_factor(db, "Transport", "Metro Rail", 0.028, "kgCO2e/p-km", "Scope 3", "DMRC / Namma Metro")
            else:
                factor, f_unit, f_src, _ = get_factor(db, "Transport", "Commuting - Diesel", 0.089, "kgCO2e/p-km", "Scope 3", "ARAI / DEFRA")

            emissions = (rec.distance_km * factor) / 1000.0
            calc = CarbonCalculation(
                assessment_id=assessment_id,
                campus_id=rec.campus_id,
                building_id=rec.building_id,
                category="Transport",
                activity=f"Commuting Transport ({rec.mode or 'Commuter Travel'})",
                scope="Scope 3",
                quantity=rec.distance_km,
                unit="passenger-km",
                emission_factor=factor,
                emission_factor_unit=f_unit,
                emission_factor_source=f_src,
                emissions_co2e=round(emissions, 4),
                calculation_method="Distance (p-km) x Commuter EF / 1000",
                data_quality=rec.data_quality,
                month=rec.month,
                year=rec.year
            )
            calculations.append(calc)

    # 3. Waste Records (Scope 3)
    waste_records = db.query(WasteRecord).filter(WasteRecord.assessment_id == assessment_id).all()
    for rec in waste_records:
        qty_kg = rec.quantity if rec.unit == "kg" else rec.quantity * 1000.0
        if rec.disposal_method == "Landfill":
            factor, f_unit, f_src, _ = get_factor(db, "Waste", "Landfill", 0.450, "kgCO2e/kg", "Scope 3", "IPCC Waste Model")
        elif rec.disposal_method == "Composting":
            factor, f_unit, f_src, _ = get_factor(db, "Waste", "Composting", 0.010, "kgCO2e/kg", "Scope 3", "DEFRA / IPCC")
        elif rec.disposal_method == "Recycling":
            factor, f_unit, f_src, _ = get_factor(db, "Waste", "Recycling", 0.021, "kgCO2e/kg", "Scope 3", "DEFRA Material Fact Sheet")
        elif rec.disposal_method == "Incineration":
            factor, f_unit, f_src, _ = get_factor(db, "Waste", "Incineration", 1.120, "kgCO2e/kg", "Scope 3", "CPCB / DEFRA")
        else:
            factor, f_unit, f_src, _ = 0.05, "kgCO2e/kg", "Default Treatment", "Scope 3"

        emissions = (qty_kg * factor) / 1000.0
        calc = CarbonCalculation(
            assessment_id=assessment_id,
            campus_id=rec.campus_id,
            building_id=rec.building_id,
            category="Waste",
            activity=f"Solid Waste Disposal ({rec.waste_type} via {rec.disposal_method})",
            scope="Scope 3",
            quantity=qty_kg,
            unit="kg",
            emission_factor=factor,
            emission_factor_unit=f_unit,
            emission_factor_source=f_src,
            emissions_co2e=round(emissions, 4),
            calculation_method=f"Waste Quantity (kg) x {rec.disposal_method} EF / 1000",
            data_quality=rec.data_quality,
            month=rec.month,
            year=rec.year
        )
        calculations.append(calc)

    # 4. Water Records (Scope 3)
    water_records = db.query(WaterRecord).filter(WaterRecord.assessment_id == assessment_id).all()
    for rec in water_records:
        qty_kl = rec.quantity if rec.unit == "kL" else (rec.quantity / 1000.0 if rec.unit == "Liters" else rec.quantity)
        if rec.source == "Borewell":
            factor, f_unit, f_src, _ = get_factor(db, "Water", "Borewell", 0.285, "kgCO2e/kL", "Scope 3", "BEE India Pumping Benchmark")
        elif rec.source == "Municipal":
            factor, f_unit, f_src, _ = get_factor(db, "Water", "Municipal", 0.344, "kgCO2e/kL", "Scope 3", "CPCB India")
        elif rec.source == "Rainwater":
            factor, f_unit, f_src, _ = 0.005, "kgCO2e/kL", "Rainwater Harvesting Low Energy", "Scope 3"
        else:
            factor, f_unit, f_src, _ = 0.150, "kgCO2e/kL", "General Water Factor", "Scope 3"

        emissions = (qty_kl * factor) / 1000.0
        calc = CarbonCalculation(
            assessment_id=assessment_id,
            campus_id=rec.campus_id,
            building_id=rec.building_id,
            category="Water",
            activity=f"Freshwater Consumption ({rec.source} - {rec.usage_type})",
            scope="Scope 3",
            quantity=qty_kl,
            unit="kL",
            emission_factor=factor,
            emission_factor_unit=f_unit,
            emission_factor_source=f_src,
            emissions_co2e=round(emissions, 4),
            calculation_method="Water Volume (kL) x Supply EF / 1000",
            data_quality=rec.data_quality,
            month=rec.month,
            year=rec.year
        )
        calculations.append(calc)

    # 5. Wastewater Records (Scope 3)
    wastewater_records = db.query(WastewaterRecord).filter(WastewaterRecord.assessment_id == assessment_id).all()
    for rec in wastewater_records:
        factor, f_unit, f_src, _ = get_factor(db, "Water", "Wastewater Treatment", 0.708, "kgCO2e/kL", "Scope 3", "CPCB / DEFRA")
        emissions = (rec.wastewater_quantity * factor) / 1000.0
        calc = CarbonCalculation(
            assessment_id=assessment_id,
            campus_id=rec.campus_id,
            building_id=rec.building_id,
            category="Water",
            activity=f"Wastewater Biological Treatment ({rec.facility_name} - {rec.treatment_type})",
            scope="Scope 3",
            quantity=rec.wastewater_quantity,
            unit="kL",
            emission_factor=factor,
            emission_factor_unit=f_unit,
            emission_factor_source=f_src,
            emissions_co2e=round(emissions, 4),
            calculation_method="Treated Sewage (kL) x STP EF / 1000",
            data_quality=rec.data_quality,
            month=rec.month,
            year=rec.year
        )
        calculations.append(calc)

    # 6. Food Records (Scope 1 LPG)
    food_records = db.query(FoodRecord).filter(FoodRecord.assessment_id == assessment_id).all()
    for rec in food_records:
        if rec.lpg_kg > 0:
            factor, f_unit, f_src, _ = get_factor(db, "Stationary Fuel", "LPG", 2.983, "kgCO2e/kg", "Scope 1", "IPCC / DEFRA")
            emissions = (rec.lpg_kg * factor) / 1000.0
            calc = CarbonCalculation(
                assessment_id=assessment_id,
                campus_id=rec.campus_id,
                building_id=rec.building_id,
                category="Stationary Fuel",
                activity=f"Canteen Cooking Fuel ({rec.canteen_name} LPG)",
                scope="Scope 1",
                quantity=rec.lpg_kg,
                unit="kg",
                emission_factor=factor,
                emission_factor_unit=f_unit,
                emission_factor_source=f_src,
                emissions_co2e=round(emissions, 4),
                calculation_method="LPG (kg) x Factor / 1000",
                data_quality="Bill/invoice",
                month=rec.month,
                year=rec.year
            )
            calculations.append(calc)

    # 7. Industrial Records (Scope 1 Process & Refrigerants)
    industrial_records = db.query(IndustrialRecord).filter(IndustrialRecord.assessment_id == assessment_id).all()
    for rec in industrial_records:
        if rec.process_emissions_tco2e > 0:
            calc = CarbonCalculation(
                assessment_id=assessment_id,
                campus_id=rec.campus_id,
                building_id=rec.building_id,
                category="Process",
                activity=f"Industrial Process Emissions ({rec.production_name})",
                scope="Scope 1",
                quantity=rec.production_quantity,
                unit=rec.production_unit,
                emission_factor=1.0,
                emission_factor_unit="tCO2e/unit",
                emission_factor_source="Direct Process Mass Balance",
                emissions_co2e=round(rec.process_emissions_tco2e, 4),
                calculation_method="Direct Mass Balance / Stoichiometric Process Measurement",
                data_quality="Measured",
                month=rec.month,
                year=rec.year
            )
            calculations.append(calc)
        if rec.refrigerant_leakage_kg > 0:
            factor, f_unit, f_src, _ = get_factor(db, "Refrigerant", rec.refrigerant_type, 2088.0, "kgCO2e/kg", "Scope 1", "IPCC AR5 GWP100")
            emissions = (rec.refrigerant_leakage_kg * factor) / 1000.0
            calc = CarbonCalculation(
                assessment_id=assessment_id,
                campus_id=rec.campus_id,
                building_id=rec.building_id,
                category="Refrigerant",
                activity=f"Refrigerant Fugitive Loss ({rec.refrigerant_type})",
                scope="Scope 1",
                quantity=rec.refrigerant_leakage_kg,
                unit="kg",
                emission_factor=factor,
                emission_factor_unit=f_unit,
                emission_factor_source=f_src,
                emissions_co2e=round(emissions, 4),
                calculation_method="Leakage (kg) x GWP100 / 1000",
                data_quality="Bill/invoice",
                month=rec.month,
                year=rec.year
            )
            calculations.append(calc)

    for calc in calculations:
        db.add(calc)

    db.commit()
    return calculations
