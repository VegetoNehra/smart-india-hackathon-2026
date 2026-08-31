"""
Configurable Risk Thresholds and Rules for Agricultural Advisory Engine.
"""

# Event Risk Level Thresholds (MVP Configuration)
PROBABILITY_THRESHOLDS = {
    "VERY_HIGH": 80.0,
    "HIGH": 60.0,
    "ELEVATED": 40.0,
    "MODERATE": 20.0,
    "LOW": 0.0
}

# False-Onset Configurable Thresholds
FALSE_ONSET_CONFIG = {
    "onset_threshold": 60.0, # Minimum Onset probability %
    "break_threshold": 50.0   # Minimum Break probability %
}

# Soil Moisture Thresholds (% VWC)
SOIL_MOISTURE_CONFIG = {
    "CRITICAL_DRY": 20.0,
    "OPTIMAL_RANGE": (25.0, 60.0),
    "WATERLOGGING_RISK": 70.0
}

def get_risk_level(prob_pct: float) -> str:
    if prob_pct >= PROBABILITY_THRESHOLDS["VERY_HIGH"]:
        return "VERY_HIGH"
    elif prob_pct >= PROBABILITY_THRESHOLDS["HIGH"]:
        return "HIGH"
    elif prob_pct >= PROBABILITY_THRESHOLDS["ELEVATED"]:
        return "ELEVATED"
    elif prob_pct >= PROBABILITY_THRESHOLDS["MODERATE"]:
        return "MODERATE"
    else:
        return "LOW"

def detect_trend(p7: float, p14: float, p21: float, p30: float) -> str:
    """
    Detects probability trend across 7D to 30D horizons.
    """
    diff = p30 - p7
    if diff >= 15.0:
        return "INCREASING"
    elif diff <= -15.0:
        return "DECREASING"
    else:
        return "STABLE"
