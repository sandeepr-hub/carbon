from sqlalchemy.orm import Session
from app.models.assessment import Assessment, AssessmentSummary
from app.models.campus import Campus, Building
from app.models.activity import EnergyRecord, RenewableRecord, WaterRecord, WasteRecord
from app.models.carbon import CarbonCalculation, CarbonReductionContribution

def aggregate_assessment_summary(db: Session, assessment_id: int):
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        return None

    campus = db.query(Campus).filter(Campus.id == assessment.campus_id).first()

    # Scope breakdowns & Gross/Positive emissions
    calcs = db.query(CarbonCalculation).filter(CarbonCalculation.assessment_id == assessment_id).all()
    scope1 = sum(c.emissions_co2e for c in calcs if c.scope == "Scope 1")
    scope2 = sum(c.emissions_co2e for c in calcs if c.scope == "Scope 2")
    scope3 = sum(c.emissions_co2e for c in calcs if c.scope == "Scope 3")
    gross = scope1 + scope2 + scope3 # POSITIVE CARBON EMISSIONS = GROSS CARBON FOOTPRINT

    # Reductions (Only Eligible status)
    reductions_records = db.query(CarbonReductionContribution).filter(
        CarbonReductionContribution.assessment_id == assessment_id,
        CarbonReductionContribution.eligibility_status == "Eligible"
    ).all()
    eligible_reductions = sum(r.reduction_co2e for r in reductions_records) # NEGATIVE CARBON FOOTPRINT
    sequestration = sum(r.reduction_co2e for r in reductions_records if r.contribution_type == "Carbon sequestration")

    net_footprint = max(0.0, gross - eligible_reductions) # NET CARBON FOOTPRINT

    # Denominators
    pop = campus.population if campus and campus.population > 0 else 1
    # Use Campus Calculated Built-up Area as denominator for area intensity
    built_up_area_sqm = campus.calculated_built_up_area_sqm if campus and campus.calculated_built_up_area_sqm > 0 else (campus.total_built_up_area_sqm if campus and campus.total_built_up_area_sqm > 0 else 1.0)

    gross_per_person = gross / pop
    red_per_person = eligible_reductions / pop
    net_per_person = net_footprint / pop

    gross_per_area = gross / built_up_area_sqm
    red_per_area = eligible_reductions / built_up_area_sqm
    net_per_area = net_footprint / built_up_area_sqm

    # Energy & Renewable metrics
    energy_recs = db.query(EnergyRecord).filter(EnergyRecord.assessment_id == assessment_id).all()
    total_grid_kwh = sum(e.quantity for e in energy_recs if "Electricity" in e.energy_type or "Grid" in e.energy_type)
    
    solar_recs = db.query(RenewableRecord).filter(RenewableRecord.assessment_id == assessment_id).all()
    solar_gen_kwh = sum(s.generation_kwh for s in solar_recs)
    displaced_grid_kwh = sum(s.displaced_grid_kwh if s.displaced_grid_kwh > 0 else s.generation_kwh for s in solar_recs)

    total_elec = total_grid_kwh + solar_gen_kwh
    renewable_pct = (solar_gen_kwh / total_elec * 100.0) if total_elec > 0 else 0.0

    # Water & Waste
    water_recs = db.query(WaterRecord).filter(WaterRecord.assessment_id == assessment_id).all()
    total_water_kl = sum(w.quantity if w.unit == "kL" else w.quantity / 1000.0 for w in water_recs)

    waste_recs = db.query(WasteRecord).filter(WasteRecord.assessment_id == assessment_id).all()
    total_waste_kg = sum(w.quantity if w.unit == "kg" else w.quantity * 1000.0 for w in waste_recs)
    diverted_waste_kg = sum(w.quantity if w.unit == "kg" else w.quantity * 1000.0 for w in waste_recs if w.disposal_method in ["Composting", "Recycling", "Reuse"])
    waste_diversion_rate = (diverted_waste_kg / total_waste_kg * 100.0) if total_waste_kg > 0 else 0.0

    # Update or create summary record
    summary = db.query(AssessmentSummary).filter(AssessmentSummary.assessment_id == assessment_id).first()
    if not summary:
        summary = AssessmentSummary(assessment_id=assessment_id)
        db.add(summary)

    summary.scope1 = round(scope1, 4)
    summary.scope2 = round(scope2, 4)
    summary.scope3 = round(scope3, 4)
    summary.gross_emissions = round(gross, 4)
    summary.eligible_reductions = round(eligible_reductions, 4)
    summary.net_footprint = round(net_footprint, 4)
    summary.sequestration = round(sequestration, 4)

    summary.population = pop
    summary.gross_per_person = round(gross_per_person, 4)
    summary.reduction_per_person = round(red_per_person, 4)
    summary.net_per_person = round(net_per_person, 4)

    summary.built_up_area_sqm = round(built_up_area_sqm, 2)
    summary.gross_per_area = round(gross_per_area, 6)
    summary.reduction_per_area = round(red_per_area, 6)
    summary.net_per_area = round(net_per_area, 6)

    summary.renewable_percentage = round(renewable_pct, 2)
    summary.grid_electricity_displaced_kwh = round(displaced_grid_kwh, 2)
    summary.total_energy_consumption_kwh = round(total_grid_kwh + solar_gen_kwh, 2)
    summary.total_water_consumption_kl = round(total_water_kl, 2)
    summary.total_waste_generated_kg = round(total_waste_kg, 2)
    summary.waste_diversion_rate = round(waste_diversion_rate, 2)

    db.commit()
    return summary

def get_building_wise_results(db: Session, assessment_id: int):
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        return []

    buildings = db.query(Building).filter(Building.campus_id == assessment.campus_id).all()
    results = []

    for b in buildings:
        calcs = db.query(CarbonCalculation).filter(
            CarbonCalculation.assessment_id == assessment_id,
            CarbonCalculation.building_id == b.id
        ).all()
        gross = sum(c.emissions_co2e for c in calcs)

        reds = db.query(CarbonReductionContribution).filter(
            CarbonReductionContribution.assessment_id == assessment_id,
            CarbonReductionContribution.building_id == b.id,
            CarbonReductionContribution.eligibility_status == "Eligible"
        ).all()
        reductions = sum(r.reduction_co2e for r in reds)
        net = max(0.0, gross - reductions)

        occ = b.occupancy if b.occupancy and b.occupancy > 0 else (b.students_on_campus + b.faculty_count + b.non_teaching_count or 1)
        area = b.built_up_area_sqm if b.built_up_area_sqm and b.built_up_area_sqm > 0 else 1.0

        results.append({
            "building_id": b.id,
            "building_code": b.building_code or f"BLD-{b.id:02d}",
            "name": b.name,
            "building_type": b.building_type,
            "floors": b.floors,
            "built_up_area_sqm": b.built_up_area_sqm,
            "occupancy": b.occupancy or (b.students_on_campus + b.faculty_count + b.non_teaching_count),
            "students_on_campus": b.students_on_campus,
            "students_off_campus": b.students_off_campus,
            "faculty_count": b.faculty_count,
            "non_teaching_count": b.non_teaching_count,
            "gross_tco2e": round(gross, 4),
            "reductions_tco2e": round(reductions, 4),
            "net_tco2e": round(net, 4),
            "co2e_per_person": round(gross / occ, 4),
            "co2e_per_sqm": round(gross / area, 6),
            "net_co2e_per_sqm": round(net / area, 6),
            "scope1_tco2e": round(sum(c.emissions_co2e for c in calcs if c.scope == "Scope 1"), 4),
            "scope2_tco2e": round(sum(c.emissions_co2e for c in calcs if c.scope == "Scope 2"), 4),
            "scope3_tco2e": round(sum(c.emissions_co2e for c in calcs if c.scope == "Scope 3"), 4)
        })

    results.sort(key=lambda x: x["gross_tco2e"], reverse=True)
    return results

def get_source_breakdown(db: Session, assessment_id: int):
    calcs = db.query(CarbonCalculation).filter(CarbonCalculation.assessment_id == assessment_id).all()
    sources = {}
    for c in calcs:
        cat = c.category
        sources[cat] = sources.get(cat, 0.0) + c.emissions_co2e

    return [{"category": k, "emissions_tco2e": round(v, 4)} for k, v in sources.items()]

def get_negative_breakdown(db: Session, assessment_id: int):
    reds = db.query(CarbonReductionContribution).filter(
        CarbonReductionContribution.assessment_id == assessment_id,
        CarbonReductionContribution.eligibility_status == "Eligible"
    ).all()
    categories = {}
    for r in reds:
        cat = r.category
        categories[cat] = categories.get(cat, 0.0) + r.reduction_co2e

    return [{"category": k, "reduction_tco2e": round(v, 4)} for k, v in categories.items()]
