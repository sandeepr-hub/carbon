from sqlalchemy.orm import Session
from app.models.assessment import Assessment, AssessmentSummary
from app.models.carbon import CarbonCalculation
from app.models.scenario import Recommendation

def generate_campus_recommendations(db: Session, assessment_id: int):
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment or not assessment.summary:
        return []

    summary = assessment.summary
    campus = assessment.campus
    calcs = db.query(CarbonCalculation).filter(CarbonCalculation.assessment_id == assessment_id).all()

    recommendations = []

    # Category totals
    cat_emissions = {}
    for c in calcs:
        cat_emissions[c.category] = cat_emissions.get(c.category, 0.0) + c.emissions_co2e

    total_gross = summary.gross_emissions if summary.gross_emissions > 0 else 1.0

    # 1. Electricity Hotspot (Scope 2)
    elec_emissions = cat_emissions.get("Electricity", 0.0)
    if (elec_emissions / total_gross) > 0.40:
        recommendations.append({
            "id": 1,
            "campus_type": campus.campus_type if campus else "All",
            "category": "Electricity",
            "title": "On-site Rooftop Solar PV Expansion & Smart Microgrid",
            "recommendation_text": f"Grid electricity accounts for {elec_emissions:.1f} tCO2e ({elec_emissions/total_gross*100:.1f}% of gross emissions). Accelerate rooftop solar PV deployment and install smart energy meters on heavy load centers (Academic & Lab buildings).",
            "intervention_type": "Emission Reduction",
            "priority": "High",
            "estimated_reduction_pct": 25.0,
            "action_type": "Renewable Energy Transition"
        })
        recommendations.append({
            "id": 2,
            "campus_type": campus.campus_type if campus else "All",
            "category": "Electricity",
            "title": "HVAC & Lighting Deep Energy Efficiency Retrofit",
            "recommendation_text": "Implement occupancy-sensor LED fixtures across all corridors and classrooms, and upgrade existing split ACs to high-efficiency BLDC/Inverter systems with smart temperature setpoint management (24°C standard).",
            "intervention_type": "Emission Reduction",
            "priority": "High",
            "estimated_reduction_pct": 15.0,
            "action_type": "Energy Efficiency Retrofit"
        })

    # 2. Transport & Fleet Hotspot
    trans_emissions = cat_emissions.get("Transport", 0.0)
    if (trans_emissions / total_gross) > 0.10:
        recommendations.append({
            "id": 3,
            "campus_type": campus.campus_type if campus else "All",
            "category": "Transport",
            "title": "Phased Fleet Electrification & EV Shuttle Network",
            "recommendation_text": f"Transportation emissions contribute {trans_emissions:.1f} tCO2e. Formulate a 3-year EV roadmap to convert internal utility vehicles, tempos, and buggies to 100% electric, paired with dedicated solar-powered EV charging infrastructure.",
            "intervention_type": "Emission Reduction",
            "priority": "High" if (trans_emissions / total_gross) > 0.20 else "Medium",
            "estimated_reduction_pct": 20.0,
            "action_type": "Mobility Electrification"
        })
        recommendations.append({
            "id": 4,
            "campus_type": campus.campus_type if campus else "All",
            "category": "Transport",
            "title": "Commuter Carpooling & Green Transit Incentive Program",
            "recommendation_text": "Encourage student and staff carpooling platforms, secure bicycle parking, and last-mile electric feeder connectivity from nearby Metro / public transit stations.",
            "intervention_type": "Emission Reduction",
            "priority": "Medium",
            "estimated_reduction_pct": 10.0,
            "action_type": "Behavioral & Policy Shift"
        })

    # 3. Waste Management & Diversion
    waste_emissions = cat_emissions.get("Waste", 0.0)
    if summary.waste_diversion_rate < 80.0:
        recommendations.append({
            "id": 5,
            "campus_type": campus.campus_type if campus else "All",
            "category": "Waste",
            "title": "Zero-Waste-to-Landfill & Decentralized Composting / Biogas",
            "recommendation_text": f"Current waste diversion is {summary.waste_diversion_rate:.1f}%. Upgrade decentralized organic waste composting/bio-methanation units near major canteens to eliminate food waste transport to landfills.",
            "intervention_type": "Emission Reduction",
            "priority": "Medium",
            "estimated_reduction_pct": 12.0,
            "action_type": "Circular Economy"
        })

    # 4. Water & Nature-based Solutions (Carbon Sequestration)
    recommendations.append({
        "id": 6,
        "campus_type": campus.campus_type if campus else "All",
        "category": "Greenery",
        "title": "Afforestation & Miyawaki Native Urban Forest Creation",
        "recommendation_text": f"Expand campus green canopy through high-density Miyawaki plantation of high-carbon-absorbing native species (Neem, Peepal, Teak). Projected to add 500+ trees sequestering an additional 11+ tCO2e/year.",
        "intervention_type": "Carbon Sequestration / Removal",
        "priority": "Medium",
        "estimated_reduction_pct": 8.0,
        "action_type": "Nature-Based Sequestration"
    })
    recommendations.append({
        "id": 7,
        "campus_type": campus.campus_type if campus else "All",
        "category": "Water",
        "title": "100% Treated Wastewater Recycling for Landscape & Flushing",
        "recommendation_text": "Ensure full utilization of central STP treated effluent for landscape irrigation, cooling towers, and dual-plumbing toilet flushing to minimize groundwater extraction energy.",
        "intervention_type": "Emission Reduction",
        "priority": "Low",
        "estimated_reduction_pct": 5.0,
        "action_type": "Resource Conservation"
    })

    return recommendations
