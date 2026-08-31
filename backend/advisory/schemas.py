from dataclasses import dataclass, field
from typing import List, Optional, Dict

@dataclass
class ForecastProbabilities:
    onset_7d: float = 0.0
    onset_14d: float = 0.0
    onset_21d: float = 0.0
    onset_30d: float = 0.0

    break_7d: float = 0.0
    break_14d: float = 0.0
    break_21d: float = 0.0
    break_30d: float = 0.0

    heavy_rain_7d: float = 0.0
    heavy_rain_14d: float = 0.0
    heavy_rain_21d: float = 0.0
    heavy_rain_30d: float = 0.0

@dataclass
class CropContext:
    crop_name: str # Rice, Maize, Cotton, Soybean
    growth_stage: str # Sowing, Establishment, Vegetative, Flowering, Grain Development, Harvest
    soil_moisture_pct: Optional[float] = None # Soil moisture percentage if available (e.g. 15.0 to 80.0)
    has_irrigation_access: bool = True

@dataclass
class AdvisoryOutput:
    risk_level: str # LOW, MODERATE, ELEVATED, HIGH, VERY_HIGH
    event_type: str # MONSOON_ONSET, BREAK_SPELL, HEAVY_RAIN, FALSE_ONSET, ROUTINE
    horizon_days: int
    probability: float
    probability_trend: str # INCREASING, DECREASING, STABLE
    false_onset_risk: bool
    crop_name: str
    growth_stage: str
    title: str
    message: str
    primary_action: str
    supporting_actions: List[str] = field(default_factory=list)
    reasoning: str = ""
    advisory_code: str = ""

    def to_dict(self) -> Dict:
        return {
            "risk_level": self.risk_level,
            "event_type": self.event_type,
            "horizon_days": self.horizon_days,
            "probability": round(self.probability, 1),
            "probability_trend": self.probability_trend,
            "false_onset_risk": self.false_onset_risk,
            "crop_name": self.crop_name,
            "growth_stage": self.growth_stage,
            "title": self.title,
            "message": self.message,
            "primary_action": self.primary_action,
            "supporting_actions": self.supporting_actions,
            "reasoning": self.reasoning,
            "advisory_code": self.advisory_code
        }
