"""
Crop and Growth Stage Catalog for Agricultural Advisory Engine.
Defines supported crops, stages, and agronomic risk sensitivity profiles.
"""

SUPPORTED_CROPS = ["Rice", "Maize", "Cotton", "Soybean"]

GROWTH_STAGES = [
    "Sowing",
    "Germination / Establishment",
    "Vegetative",
    "Flowering",
    "Grain/Fruit Development",
    "Harvest"
]

CROP_PROFILES = {
    "Rice": {
        "water_demand": "High",
        "break_sensitive_stages": ["Sowing", "Germination / Establishment", "Flowering"],
        "heavy_rain_sensitive_stages": ["Harvest", "Sowing"]
    },
    "Maize": {
        "water_demand": "Moderate",
        "break_sensitive_stages": ["Sowing", "Flowering"],
        "heavy_rain_sensitive_stages": ["Germination / Establishment", "Harvest"]
    },
    "Cotton": {
        "water_demand": "Moderate",
        "break_sensitive_stages": ["Germination / Establishment", "Flowering"],
        "heavy_rain_sensitive_stages": ["Vegetative", "Flowering", "Harvest"]
    },
    "Soybean": {
        "water_demand": "Moderate",
        "break_sensitive_stages": ["Sowing", "Flowering"],
        "heavy_rain_sensitive_stages": ["Germination / Establishment", "Harvest"]
    }
}
