"""
Core Deterministic Agricultural Advisory Engine.
Translates probabilistic event predictions into actionable, crop-specific recommendations.
"""

from typing import Dict, Optional

try:
    from advisory.schemas import ForecastProbabilities, CropContext, AdvisoryOutput
    from advisory.rules import get_risk_level, detect_trend, FALSE_ONSET_CONFIG, SOIL_MOISTURE_CONFIG
    from advisory.crops import CROP_PROFILES
except ImportError:
    from backend.advisory.schemas import ForecastProbabilities, CropContext, AdvisoryOutput
    from backend.advisory.rules import get_risk_level, detect_trend, FALSE_ONSET_CONFIG, SOIL_MOISTURE_CONFIG
    from backend.advisory.crops import CROP_PROFILES

class AdvisoryEngine:
    def __init__(self, false_onset_onset_thresh: float = 60.0, false_onset_break_thresh: float = 50.0):
        self.false_onset_onset_thresh = false_onset_onset_thresh
        self.false_onset_break_thresh = false_onset_break_thresh

    def generate_advisory(self, forecast: ForecastProbabilities, crop_ctx: CropContext) -> AdvisoryOutput:
        """
        Executes deterministic rule hierarchy to produce structured AdvisoryOutput.
        """
        crop_name = crop_ctx.crop_name
        stage = crop_ctx.growth_stage
        sm = crop_ctx.soil_moisture_pct

        # Extract peak probabilities & horizons
        onset_max = max(forecast.onset_7d, forecast.onset_14d, forecast.onset_21d, forecast.onset_30d)
        break_max = max(forecast.break_7d, forecast.break_14d, forecast.break_21d, forecast.break_30d)
        heavy_max = max(forecast.heavy_rain_7d, forecast.heavy_rain_14d, forecast.heavy_rain_21d, forecast.heavy_rain_30d)

        # Detect trends
        onset_trend = detect_trend(forecast.onset_7d, forecast.onset_14d, forecast.onset_21d, forecast.onset_30d)
        break_trend = detect_trend(forecast.break_7d, forecast.break_14d, forecast.break_21d, forecast.break_30d)
        heavy_trend = detect_trend(forecast.heavy_rain_7d, forecast.heavy_rain_14d, forecast.heavy_rain_21d, forecast.heavy_rain_30d)

        # Check False-Onset Risk Condition
        is_false_onset = (forecast.onset_14d >= self.false_onset_onset_thresh) and (forecast.break_14d >= self.false_onset_break_thresh)

        # -------------------------------------------------------------
        # RULE HIERARCHY & PRIORITY RANKING
        # -------------------------------------------------------------

        # PRIORITY 1: FALSE-ONSET RISK (Conflicting Onset + Break)
        if is_false_onset:
            risk_lvl = get_risk_level(max(forecast.onset_14d, forecast.break_14d))
            return AdvisoryOutput(
                risk_level=risk_lvl,
                event_type="FALSE_ONSET",
                horizon_days=14,
                probability=forecast.onset_14d,
                probability_trend=onset_trend,
                false_onset_risk=True,
                crop_name=crop_name,
                growth_stage=stage,
                title="⚠️ False-Onset Risk Warning",
                message=f"Monsoon onset appears likely ({forecast.onset_14d:.0f}%), but break-spell risk remains high ({forecast.break_14d:.0f}%) over the next 14 days.",
                primary_action=f"Avoid relying solely on initial rainfall for {crop_name} {stage.lower()}. Delay rain-dependent sowing until sustained moisture settles.",
                supporting_actions=[
                    "Prepare supplemental irrigation alternatives",
                    "Monitor soil moisture before committing seed"
                ],
                reasoning=f"Onset 14D ({forecast.onset_14d:.0f}%) >= {self.false_onset_onset_thresh}% AND Break 14D ({forecast.break_14d:.0f}%) >= {self.false_onset_break_thresh}%. High risk of early dry spell after initial rain.",
                advisory_code="FALSE_ONSET_WARNING"
            )

        # PRIORITY 2: HEAVY RAIN THREAT
        if heavy_max >= 60.0:
            horizon = 7 if forecast.heavy_rain_7d >= 60.0 else 14
            prob = forecast.heavy_rain_7d if horizon == 7 else forecast.heavy_rain_14d
            risk_lvl = get_risk_level(prob)

            actions = [
                "Ensure drainage channels are clear of debris",
                "Protect harvested produce and field inputs from water exposure"
            ]
            if sm is not None and sm >= SOIL_MOISTURE_CONFIG["WATERLOGGING_RISK"]:
                actions.append("Critical waterlogging risk: refrain from all field irrigation")

            return AdvisoryOutput(
                risk_level=risk_lvl,
                event_type="HEAVY_RAIN",
                horizon_days=horizon,
                probability=prob,
                probability_trend=heavy_trend,
                false_onset_risk=False,
                crop_name=crop_name,
                growth_stage=stage,
                title="⚡ High Heavy Rainfall Alert",
                message=f"Heavy rainfall event probability is {prob:.0f}% over the next {horizon} days.",
                primary_action=f"Check and clear field drainage systems for {crop_name} ({stage}) to prevent waterlogging.",
                supporting_actions=actions,
                reasoning=f"Heavy Rain probability ({prob:.0f}%) exceeded high threshold (60%) at horizon {horizon}D.",
                advisory_code="HEAVY_RAIN_WARNING"
            )

        # PRIORITY 3: BREAK SPELL (DRY SPELL THREAT)
        if break_max >= 60.0:
            horizon = 7 if forecast.break_7d >= 60.0 else (14 if forecast.break_14d >= 60.0 else 21)
            prob = forecast.break_7d if horizon == 7 else (forecast.break_14d if horizon == 14 else forecast.break_21d)
            risk_lvl = get_risk_level(prob)

            if "Sowing" in stage or "Establishment" in stage:
                primary = f"Delay rain-dependent {crop_name} sowing if practical due to imminent dry spell."
                supp = ["Prepare supplemental irrigation facilities", "Keep nursery beds covered and hydrated"]
            else:
                if sm is not None and sm <= SOIL_MOISTURE_CONFIG["CRITICAL_DRY"]:
                    primary = f"Soil moisture is critically low ({sm:.0f}%). Execute supplemental irrigation immediately for {crop_name} ({stage})."
                else:
                    primary = f"Prepare supplemental irrigation systems for {crop_name} ({stage}) to buffer against dry spell."
                supp = ["Monitor soil moisture daily", "Apply organic mulch to conserve root-zone moisture"]

            return AdvisoryOutput(
                risk_level=risk_lvl,
                event_type="BREAK_SPELL",
                horizon_days=horizon,
                probability=prob,
                probability_trend=break_trend,
                false_onset_risk=False,
                crop_name=crop_name,
                growth_stage=stage,
                title="🟠 High Dry-Spell Risk",
                message=f"A prolonged dry spell (break spell) is likely ({prob:.0f}%) over the next {horizon} days.",
                primary_action=primary,
                supporting_actions=supp,
                reasoning=f"Break Spell probability ({prob:.0f}%) exceeded threshold (60%) at horizon {horizon}D.",
                advisory_code="BREAK_SPELL_WARNING"
            )

        # PRIORITY 4: MONSOON ONSET FAVORABLE
        if onset_max >= 60.0:
            horizon = 7 if forecast.onset_7d >= 60.0 else 14
            prob = forecast.onset_7d if horizon == 7 else forecast.onset_14d
            risk_lvl = get_risk_level(prob)

            return AdvisoryOutput(
                risk_level=risk_lvl,
                event_type="MONSOON_ONSET",
                horizon_days=horizon,
                probability=prob,
                probability_trend=onset_trend,
                false_onset_risk=False,
                crop_name=crop_name,
                growth_stage=stage,
                title="🟢 Favorable Monsoon Onset Alert",
                message=f"Monsoon onset probability is favorable ({prob:.0f}%) over the next {horizon} days.",
                primary_action=f"Prepare land and seed stocks for {crop_name} {stage.lower()} as soil moisture conditions settle.",
                supporting_actions=[
                    "Finalize seed treatment and land preparation",
                    "Verify field drainage readiness before sowing"
                ],
                reasoning=f"Monsoon Onset probability ({prob:.0f}%) is high with low break-spell conflict.",
                advisory_code="ONSET_FAVORABLE"
            )

        # PRIORITY 5: ROUTINE MONITORING (LOW / MODERATE RISK)
        return AdvisoryOutput(
            risk_level="LOW",
            event_type="ROUTINE",
            horizon_days=7,
            probability=max(forecast.onset_7d, forecast.break_7d, forecast.heavy_rain_7d),
            probability_trend="STABLE",
            false_onset_risk=False,
            crop_name=crop_name,
            growth_stage=stage,
            title="ℹ️ Routine Weather Monitoring",
            message="No immediate extreme weather risk detected over the next 7–14 days.",
            primary_action=f"Continue standard field practices for {crop_name} ({stage}).",
            supporting_actions=[
                "Maintain routine field inspections",
                "Check weekly weather updates regularly"
            ],
            reasoning="All event probabilities remain below high alert thresholds.",
            advisory_code="ROUTINE_MONITORING"
        )
