def check_solar_double_counting(is_onsite_consumed: bool):
    """
    Safeguard Rule:
    If solar generation is consumed on-site, it already directly replaces purchased grid electricity,
    reducing Scope 2 gross emissions.
    Subtracting it again as a separate negative emission would constitute illegal double-counting.
    """
    if is_onsite_consumed:
        return False, "On-site solar electricity directly replaces grid electricity imports, reducing Scope 2 emissions at the source. It must not be counted again as a separate negative offset."
    return True, "Exported clean power displacing external grid generation is eligible under verifiable grid-displacement protocols."

def validate_activity_quantity(field_name: str, quantity: float):
    """
    Safeguard Rule:
    Activity data fields must never accept negative numbers to simulate reductions.
    Reductions must strictly be logged in the dedicated reduction contribution ledger.
    """
    if quantity < 0:
        raise ValueError(f"Invalid activity quantity for '{field_name}': {quantity}. Negative values are strictly forbidden in activity data. Use the reduction ledger for verifiable removals/reductions.")
    return True

def explain_negative_net_balance(gross: float, reductions: float):
    """
    Safeguard Rule:
    If reductions exceed gross emissions, provide transparent explanatory disclosure.
    """
    if reductions > gross:
        diff = reductions - gross
        return {
            "is_negative": True,
            "net_balance": round(-diff, 4),
            "label": "Net balance after eligible reductions and removals",
            "warning": "A negative net carbon balance indicates eligible reductions and sequestration exceed gross operational emissions. This is methodology-dependent and does not by itself confer certified carbon neutrality without third-party boundary verification."
        }
    return {
        "is_negative": False,
        "net_balance": round(gross - reductions, 4),
        "label": "Net Carbon Footprint",
        "warning": None
    }
