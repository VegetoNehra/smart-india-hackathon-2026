"""
Core Deterministic Agricultural Advisory Engine.
Translates probabilistic event predictions into actionable, crop-specific recommendations.
"""

from typing import Dict, Optional

try:
    from advisory.schemas import ForecastProbabilities, CropContext, AdvisoryOutput
    from advisory.rules import get_risk_level, detect_trend, FALSE_ONSET_CONFIG, SOIL_MOISTURE_CONFIG
    from advisory.crops import generate_crop_stage_action
except ImportError:
    from backend.advisory.schemas import ForecastProbabilities, CropContext, AdvisoryOutput
    from backend.advisory.rules import get_risk_level, detect_trend, FALSE_ONSET_CONFIG, SOIL_MOISTURE_CONFIG
    from backend.advisory.crops import generate_crop_stage_action

class AdvisoryEngine:
    def __init__(self, false_onset_onset_thresh: float = 60.0, false_onset_break_thresh: float = 50.0):
        self.false_onset_onset_thresh = false_onset_onset_thresh
        self.false_onset_break_thresh = false_onset_break_thresh

    def generate_advisory(self, forecast: ForecastProbabilities, crop_ctx: CropContext, lang: str = "en") -> AdvisoryOutput:
        """
        Executes deterministic rule hierarchy to produce structured AdvisoryOutput.
        Supports English ('en') and Hindi ('hi').
        """
        crop_name = crop_ctx.crop_name
        stage = crop_ctx.growth_stage
        sm = crop_ctx.soil_moisture_pct
        is_hi = (lang == "hi")

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
            primary, supp = generate_crop_stage_action(crop_name, stage, "FALSE_ONSET", sm, lang=lang)
            return AdvisoryOutput(
                risk_level=risk_lvl,
                event_type="FALSE_ONSET",
                horizon_days=14,
                probability=forecast.onset_14d,
                probability_trend=onset_trend,
                false_onset_risk=True,
                crop_name=crop_name,
                growth_stage=stage,
                title="⚠️ झूठे-आगमन (False-Onset) का जोखिम" if is_hi else "⚠️ False-Onset Risk Warning",
                message=f"मानसून का आगमन संभावित है ({forecast.onset_14d:.0f}%), लेकिन अगले 14 दिनों में सूखा काल का जोखिम उच्च है ({forecast.break_14d:.0f}%)।" if is_hi else f"Monsoon onset appears likely ({forecast.onset_14d:.0f}%), but break-spell risk remains high ({forecast.break_14d:.0f}%) over the next 14 days.",
                primary_action=primary,
                supporting_actions=supp,
                reasoning=f"Onset 14D ({forecast.onset_14d:.0f}%) >= {self.false_onset_onset_thresh}% AND Break 14D ({forecast.break_14d:.0f}%) >= {self.false_onset_break_thresh}%. High risk of early dry spell after initial rain.",
                advisory_code="FALSE_ONSET_WARNING"
            )

        # PRIORITY 2: HEAVY RAIN THREAT
        if heavy_max >= 60.0:
            horizon = 7 if forecast.heavy_rain_7d >= 60.0 else 14
            prob = forecast.heavy_rain_7d if horizon == 7 else forecast.heavy_rain_14d
            risk_lvl = get_risk_level(prob)
            primary, supp = generate_crop_stage_action(crop_name, stage, "HEAVY_RAIN", sm, lang=lang)

            return AdvisoryOutput(
                risk_level=risk_lvl,
                event_type="HEAVY_RAIN",
                horizon_days=horizon,
                probability=prob,
                probability_trend=heavy_trend,
                false_onset_risk=False,
                crop_name=crop_name,
                growth_stage=stage,
                title="⚡ भारी बारिश की चेतावनी" if is_hi else "⚡ High Heavy Rainfall Alert",
                message=f"अगले {horizon} दिनों में भारी बारिश की संभावना {prob:.0f}% है।" if is_hi else f"Heavy rainfall event probability is {prob:.0f}% over the next {horizon} days.",
                primary_action=primary,
                supporting_actions=supp,
                reasoning=f"Heavy Rain probability ({prob:.0f}%) exceeded high threshold (60%) at horizon {horizon}D.",
                advisory_code="HEAVY_RAIN_WARNING"
            )

        # PRIORITY 3: BREAK SPELL (DRY SPELL THREAT)
        if break_max >= 60.0:
            horizon = 7 if forecast.break_7d >= 60.0 else (14 if forecast.break_14d >= 60.0 else 21)
            prob = forecast.break_7d if horizon == 7 else (forecast.break_14d if horizon == 14 else forecast.break_21d)
            risk_lvl = get_risk_level(prob)
            primary, supp = generate_crop_stage_action(crop_name, stage, "BREAK_SPELL", sm, lang=lang)

            return AdvisoryOutput(
                risk_level=risk_lvl,
                event_type="BREAK_SPELL",
                horizon_days=horizon,
                probability=prob,
                probability_trend=break_trend,
                false_onset_risk=False,
                crop_name=crop_name,
                growth_stage=stage,
                title="🟠 उच्च सूखा काल (Break-Spell) जोखिम" if is_hi else "🟠 High Dry-Spell Risk",
                message=f"अगले {horizon} दिनों में लंबा सूखा काल संभावित है ({prob:.0f}%)।" if is_hi else f"A prolonged dry spell (break spell) is likely ({prob:.0f}%) over the next {horizon} days.",
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
            primary, supp = generate_crop_stage_action(crop_name, stage, "MONSOON_ONSET", sm, lang=lang)

            return AdvisoryOutput(
                risk_level=risk_lvl,
                event_type="MONSOON_ONSET",
                horizon_days=horizon,
                probability=prob,
                probability_trend=onset_trend,
                false_onset_risk=False,
                crop_name=crop_name,
                growth_stage=stage,
                title="🟢 अनुकूल मानसून आगमन चेतावनी" if is_hi else "🟢 Favorable Monsoon Onset Alert",
                message=f"अगले {horizon} दिनों में मानसून आगमन की संभावना अनुकूल है ({prob:.0f}%)।" if is_hi else f"Monsoon onset probability is favorable ({prob:.0f}%) over the next {horizon} days.",
                primary_action=primary,
                supporting_actions=supp,
                reasoning=f"Monsoon Onset probability ({prob:.0f}%) is high with low break-spell conflict.",
                advisory_code="ONSET_FAVORABLE"
            )

        # PRIORITY 5: ROUTINE MONITORING (LOW / MODERATE RISK)
        primary, supp = generate_crop_stage_action(crop_name, stage, "ROUTINE", sm, lang=lang)
        return AdvisoryOutput(
            risk_level="LOW",
            event_type="ROUTINE",
            horizon_days=7,
            probability=max(forecast.onset_7d, forecast.break_7d, forecast.heavy_rain_7d),
            probability_trend="STABLE",
            false_onset_risk=False,
            crop_name=crop_name,
            growth_stage=stage,
            title="ℹ️ नियमित मौसम निगरानी" if is_hi else "ℹ️ Routine Weather Monitoring",
            message="अगले 7–14 दिनों में कोई तात्कालिक गंभीर मौसम जोखिम नहीं है।" if is_hi else "No immediate extreme weather risk detected over the next 7–14 days.",
            primary_action=primary,
            supporting_actions=supp,
            reasoning="All event probabilities remain below high alert thresholds.",
            advisory_code="ROUTINE_MONITORING"
        )
