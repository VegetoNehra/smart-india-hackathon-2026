import sys
import os

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.advisory.schemas import ForecastProbabilities, CropContext
from backend.advisory.engine import AdvisoryEngine

def test_advisory_scenarios():
    engine = AdvisoryEngine()

    print("==========================================================")
    print("RUNNING AGRICULTURAL ADVISORY ENGINE UNIT TEST SUITE")
    print("==========================================================")

    # ---------------------------------------------------------
    # SCENARIO 1: High Onset, Low Break (Favorable Onset)
    # ---------------------------------------------------------
    print("\n--- SCENARIO 1: High Onset (80%), Low Break (20%) ---")
    fc1 = ForecastProbabilities(
        onset_7d=80.0, onset_14d=85.0, onset_21d=85.0, onset_30d=85.0,
        break_7d=20.0, break_14d=20.0, break_21d=15.0, break_30d=10.0,
        heavy_rain_7d=10.0, heavy_rain_14d=15.0, heavy_rain_21d=15.0, heavy_rain_30d=15.0
    )
    crop1 = CropContext(crop_name="Rice", growth_stage="Sowing")
    adv1 = engine.generate_advisory(fc1, crop1)

    assert adv1.advisory_code == "ONSET_FAVORABLE", f"Expected ONSET_FAVORABLE, got {adv1.advisory_code}"
    assert adv1.false_onset_risk == False
    assert "Rice" in adv1.primary_action
    print(f"[PASS] Code: {adv1.advisory_code} | Title: {adv1.title.encode('ascii', 'replace').decode('ascii')}")
    print(f"       Action: {adv1.primary_action.encode('ascii', 'replace').decode('ascii')}")
    
    # ---------------------------------------------------------
    # SCENARIO 2: High Onset (75%) + High Break (70%) -> False-Onset Risk
    # ---------------------------------------------------------
    print("\n--- SCENARIO 2: High Onset (75%) + High Break (70%) -> False-Onset Warning ---")
    fc2 = ForecastProbabilities(
        onset_7d=75.0, onset_14d=80.0, onset_21d=80.0, onset_30d=80.0,
        break_7d=65.0, break_14d=70.0, break_21d=75.0, break_30d=80.0,
        heavy_rain_7d=10.0, heavy_rain_14d=15.0, heavy_rain_21d=15.0, heavy_rain_30d=15.0
    )
    crop2 = CropContext(crop_name="Rice", growth_stage="Sowing")
    adv2 = engine.generate_advisory(fc2, crop2)

    assert adv2.advisory_code == "FALSE_ONSET_WARNING", f"Expected FALSE_ONSET_WARNING, got {adv2.advisory_code}"
    assert adv2.false_onset_risk == True
    assert "Delay" in adv2.primary_action or "Avoid" in adv2.primary_action
    print(f"[PASS] Code: {adv2.advisory_code} | Title: {adv2.title.encode('ascii', 'replace').decode('ascii')}")
    print(f"       Action: {adv2.primary_action.encode('ascii', 'replace').decode('ascii')}")

    # ---------------------------------------------------------
    # SCENARIO 3: Heavy Rain (75%), Cotton + Vegetative
    # ---------------------------------------------------------
    print("\n--- SCENARIO 3: Heavy Rain (75%), Cotton + Vegetative ---")
    fc3 = ForecastProbabilities(
        onset_7d=30.0, onset_14d=35.0, onset_21d=40.0, onset_30d=40.0,
        break_7d=15.0, break_14d=20.0, break_21d=20.0, break_30d=20.0,
        heavy_rain_7d=75.0, heavy_rain_14d=80.0, heavy_rain_21d=60.0, heavy_rain_30d=50.0
    )
    crop3 = CropContext(crop_name="Cotton", growth_stage="Vegetative", soil_moisture_pct=75.0)
    adv3 = engine.generate_advisory(fc3, crop3)

    assert adv3.advisory_code == "HEAVY_RAIN_WARNING", f"Expected HEAVY_RAIN_WARNING, got {adv3.advisory_code}"
    assert "drainage" in adv3.primary_action.lower() or "furrow" in adv3.primary_action.lower()
    print(f"[PASS] Code: {adv3.advisory_code} | Title: {adv3.title.encode('ascii', 'replace').decode('ascii')}")
    print(f"       Action: {adv3.primary_action.encode('ascii', 'replace').decode('ascii')}")

    # ---------------------------------------------------------
    # SCENARIO 4: High Break (75%), Wheat + Flowering
    # ---------------------------------------------------------
    print("\n--- SCENARIO 4: High Break (75%), Wheat + Flowering ---")
    fc4 = ForecastProbabilities(
        onset_7d=20.0, onset_14d=20.0, onset_21d=20.0, onset_30d=20.0,
        break_7d=75.0, break_14d=80.0, break_21d=85.0, break_30d=85.0,
        heavy_rain_7d=5.0, heavy_rain_14d=5.0, heavy_rain_21d=5.0, heavy_rain_30d=5.0
    )
    crop4 = CropContext(crop_name="Wheat", growth_stage="Flowering")
    adv4 = engine.generate_advisory(fc4, crop4)

    assert adv4.advisory_code == "BREAK_SPELL_WARNING", f"Expected BREAK_SPELL_WARNING, got {adv4.advisory_code}"
    assert "Wheat" in adv4.primary_action or "irrigation" in adv4.primary_action.lower()
    print(f"[PASS] Code: {adv4.advisory_code} | Title: {adv4.title.encode('ascii', 'replace').decode('ascii')}")
    print(f"       Action: {adv4.primary_action.encode('ascii', 'replace').decode('ascii')}")

    # ---------------------------------------------------------
    # SCENARIO 5: Heavy Rain (75%), Potato + Harvest
    # ---------------------------------------------------------
    print("\n--- SCENARIO 5: Heavy Rain (75%), Potato + Harvest ---")
    fc5 = ForecastProbabilities(
        heavy_rain_7d=75.0, heavy_rain_14d=80.0
    )
    crop5 = CropContext(crop_name="Potato", growth_stage="Harvest")
    adv5 = engine.generate_advisory(fc5, crop5)

    assert adv5.advisory_code == "HEAVY_RAIN_WARNING"
    assert "Postpone" in adv5.primary_action or "harvesting" in adv5.primary_action
    print(f"[PASS] Code: {adv5.advisory_code} | Title: {adv5.title.encode('ascii', 'replace').decode('ascii')}")
    print(f"       Action: {adv5.primary_action.encode('ascii', 'replace').decode('ascii')}")

    # ---------------------------------------------------------
    # SCENARIO 6: Hindi Language Generation Test (Break Spell, Sugarcane + Flowering)
    # ---------------------------------------------------------
    print("\n--- SCENARIO 6: Hindi Language Test (Break Spell, Sugarcane + Flowering) ---")
    fc6 = ForecastProbabilities(break_7d=75.0, break_14d=80.0)
    crop6 = CropContext(crop_name="Sugarcane", growth_stage="Flowering")
    adv6 = engine.generate_advisory(fc6, crop6, lang="hi")

    assert adv6.advisory_code == "BREAK_SPELL_WARNING"
    assert "सिंचाई" in adv6.primary_action or "अवस्था" in adv6.primary_action
    print(f"[PASS] Code: {adv6.advisory_code} | Title (HI): {adv6.title.encode('ascii', 'replace').decode('ascii')}")
    print(f"       Action (HI): {adv6.primary_action.encode('ascii', 'replace').decode('ascii')}")

    print("\n==========================================================")
    print("ALL 6 UNIT TEST SCENARIOS PASSED SUCCESSFULLY (100% PASS)!")
    print("==========================================================")

if __name__ == '__main__':
    test_advisory_scenarios()
