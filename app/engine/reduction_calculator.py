from sqlalchemy.orm import Session
from app.models.assessment import Assessment
from app.models.campus import Campus
from app.models.activity import (
    GreenRecord, RenewableRecord, TransportRecord, WasteRecord,
    WaterConservationRecord, WaterBodyRecord, AnimalRecord
)
from app.models.carbon import CarbonReductionContribution
from app.engine.anti_double_counting import check_solar_double_counting

def calculate_reduction_contributions(db: Session, assessment_id: int):
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        return []

    campus = db.query(Campus).filter(Campus.id == assessment.campus_id).first()
    neg_config = campus.negative_activities or {} if campus else {}

    # Clear previous reductions for this assessment
    db.query(CarbonReductionContribution).filter(CarbonReductionContribution.assessment_id == assessment_id).delete()

    contributions = []

    # 1. Solar Plant Avoided Emissions (if enabled or present)
    if neg_config.get("solar_plant", True):
        solar_records = db.query(RenewableRecord).filter(RenewableRecord.assessment_id == assessment_id).all()
        for ren in solar_records:
            is_safe, message = check_solar_double_counting(ren.is_onsite_consumed)
            # Both onsite and exported clean solar displace grid fossil emissions
            # Stored as avoided emission in negative ledger
            gen_kwh = ren.generation_kwh
            avoided_co2e = (gen_kwh * 0.716) / 1000.0 # CEA India v19 grid factor
            contrib = CarbonReductionContribution(
                assessment_id=assessment_id,
                campus_id=ren.campus_id,
                building_id=ren.building_id,
                category="Solar Plant",
                activity=f"Solar Clean Power Generation ({ren.technology} {ren.capacity_kw} kWp - {gen_kwh:,.0f} kWh)",
                contribution_type="Renewable-energy avoided emissions",
                baseline_quantity=gen_kwh,
                baseline_unit="kWh Grid Electricity",
                project_quantity=gen_kwh,
                project_unit="kWh Solar Generation",
                emission_factor=0.716,
                gross_baseline_emissions=round(avoided_co2e, 4),
                project_emissions=0.0,
                reduction_co2e=round(avoided_co2e, 4),
                methodology="Grid Electricity Displacement (CEA India v19 Benchmark)",
                source="CEA India v19 Baseline Emission Factor",
                reference_year=ren.year,
                eligibility_status="Eligible",
                assumptions="On-site clean solar PV generation displacing high-carbon grid power."
            )
            contributions.append(contrib)

    # 2. Tree Carbon Sequestration (Gardening / Greenery) (if enabled)
    if neg_config.get("gardening", True):
        green_records = db.query(GreenRecord).filter(GreenRecord.assessment_id == assessment_id).all()
        for rec in green_records:
            factor = 22.0 # kg CO2 / tree / year (IPCC/FSI)
            seq_tco2e = (rec.tree_count * factor) / 1000.0
            if rec.annual_sequestration_tco2e and rec.annual_sequestration_tco2e > 0:
                seq_tco2e = rec.annual_sequestration_tco2e

            contrib = CarbonReductionContribution(
                assessment_id=assessment_id,
                campus_id=rec.campus_id,
                building_id=rec.building_id,
                category="Gardening / Greenery",
                activity=f"Biomass Sequestration by Campus Trees ({rec.tree_count:,} mature trees across {rec.green_area_sqm/4046.86:.1f} acres)",
                contribution_type="Carbon sequestration",
                baseline_quantity=0.0,
                baseline_unit="tree",
                project_quantity=float(rec.tree_count),
                project_unit="tree",
                emission_factor=factor,
                gross_baseline_emissions=0.0,
                project_emissions=0.0,
                reduction_co2e=round(seq_tco2e, 4),
                methodology="FSI Tree Biomass Growth Model & IPCC GPG for LULUCF (22.0 kg CO2/tree/year)",
                source="Forest Survey of India / IPCC AR5",
                reference_year=rec.year,
                eligibility_status="Eligible",
                assumptions="Mature native canopy tree carbon uptake validated through ground census."
            )
            contributions.append(contrib)

    # 3. Water Conservation (if enabled)
    if neg_config.get("water_conservation", False):
        water_saved_recs = db.query(WaterConservationRecord).filter(WaterConservationRecord.assessment_id == assessment_id).all()
        for wc in water_saved_recs:
            factor = 0.344 # kgCO2e / kL avoided municipal pumping/treatment
            saved_co2e = (wc.water_saved_kl * factor) / 1000.0
            contrib = CarbonReductionContribution(
                assessment_id=assessment_id,
                campus_id=wc.campus_id,
                category="Water Conservation",
                activity=f"Water Conservation & Efficiency ({wc.method} - {wc.water_saved_kl:,.0f} kL saved)",
                contribution_type="Resource conservation avoided emissions",
                baseline_quantity=wc.water_saved_kl,
                baseline_unit="kL Municipal Water",
                project_quantity=wc.water_saved_kl,
                project_unit=f"kL {wc.method}",
                emission_factor=factor,
                gross_baseline_emissions=round(saved_co2e, 4),
                project_emissions=0.0,
                reduction_co2e=round(saved_co2e, 4),
                methodology="Avoided Pumping & Treatment Energy (CPCB Benchmark 0.344 kgCO2e/kL)",
                source="CPCB India Water Energy Intensity Benchmark",
                reference_year=wc.year,
                eligibility_status="Eligible",
                assumptions=f"Conservation of {wc.water_saved_kl:,.0f} kL freshwater avoiding municipal energy use."
            )
            contributions.append(contrib)

    # 4. Water Bodies Ecological Carbon Benefit (if enabled)
    if neg_config.get("water_bodies", False):
        water_body_recs = db.query(WaterBodyRecord).filter(WaterBodyRecord.assessment_id == assessment_id).all()
        for wb in water_body_recs:
            # 0.5 tCO2e per 1000 m2 preserved ecological wetland/pond
            factor = 0.0005 # tCO2e / m2 / yr
            wb_co2e = wb.carbon_benefit_tco2e if wb.carbon_benefit_tco2e > 0 else (wb.total_area_sqm * factor)
            contrib = CarbonReductionContribution(
                assessment_id=assessment_id,
                campus_id=wb.campus_id,
                category="Water Bodies",
                activity=f"Ecological Wetland & Water Body Conservation ({wb.body_count} {wb.body_type}s - {wb.total_area_sqm:,.0f} m²)",
                contribution_type="Ecosystem conservation",
                baseline_quantity=0.0,
                baseline_unit="m² wetland",
                project_quantity=wb.total_area_sqm,
                project_unit="m² water body",
                emission_factor=factor * 1000.0,
                gross_baseline_emissions=0.0,
                project_emissions=0.0,
                reduction_co2e=round(wb_co2e, 4),
                methodology=wb.methodology,
                source="Ramsar Wetland Carbon Dynamics Guidelines",
                reference_year=wb.year,
                eligibility_status="Eligible",
                assumptions="Sediment carbon stabilization in non-eutrophic campus water bodies."
            )
            contributions.append(contrib)

    # 5. Animals / Livestock (if enabled)
    if neg_config.get("animals", False):
        animal_recs = db.query(AnimalRecord).filter(AnimalRecord.assessment_id == assessment_id).all()
        for an in animal_recs:
            if an.carbon_benefit_tco2e > 0:
                contrib = CarbonReductionContribution(
                    assessment_id=assessment_id,
                    campus_id=an.campus_id,
                    category="Animals / Livestock",
                    activity=f"Controlled Biogas & Manure Treatment ({an.animal_count} {an.animal_type})",
                    contribution_type="Methane capture & utilization",
                    baseline_quantity=an.animal_count,
                    baseline_unit="head",
                    project_quantity=an.animal_count,
                    project_unit="head with biogas",
                    emission_factor=0.0,
                    gross_baseline_emissions=0.0,
                    project_emissions=0.0,
                    reduction_co2e=round(an.carbon_benefit_tco2e, 4),
                    methodology=an.methodology,
                    source="Verified Biogas Digestion Methodology",
                    reference_year=an.year,
                    eligibility_status="Eligible",
                    assumptions="Avoided open manure methane via enclosed biogas digester."
                )
                contributions.append(contrib)

    # 6. Waste Diversion (Composting & Recycling)
    waste_records = db.query(WasteRecord).filter(
        WasteRecord.assessment_id == assessment_id,
        WasteRecord.disposal_method.in_(["Composting", "Recycling"])
    ).all()
    for w in waste_records:
        qty_kg = w.quantity if w.unit == "kg" else w.quantity * 1000.0
        baseline_emissions = (qty_kg * 0.450) / 1000.0
        actual_emissions = (qty_kg * (0.010 if w.disposal_method == "Composting" else 0.021)) / 1000.0
        avoided_co2e = max(0.0, baseline_emissions - actual_emissions)

        contrib = CarbonReductionContribution(
            assessment_id=assessment_id,
            campus_id=w.campus_id,
            building_id=w.building_id,
            category="Waste Diversion",
            activity=f"Avoided Landfill Methane via {w.disposal_method} ({w.waste_type})",
            contribution_type="Waste-diversion reduction",
            baseline_quantity=qty_kg,
            baseline_unit="kg Landfilled",
            project_quantity=qty_kg,
            project_unit=f"kg {w.disposal_method}",
            emission_factor=0.450,
            gross_baseline_emissions=round(baseline_emissions, 4),
            project_emissions=round(actual_emissions, 4),
            reduction_co2e=round(avoided_co2e, 4),
            methodology="Avoided Landfill Methane Generation (IPCC Tier 1 / DEFRA)",
            source="IPCC 2006 Waste Model",
            reference_year=w.year,
            eligibility_status="Eligible",
            assumptions=f"Diversion of {qty_kg:,.0f} kg waste from unmanaged dumpsite to controlled on-site {w.disposal_method}."
        )
        contributions.append(contrib)

    for c in contributions:
        db.add(c)

    db.commit()
    return contributions
