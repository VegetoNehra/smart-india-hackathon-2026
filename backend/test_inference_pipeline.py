import sys
import os

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.inference_pipeline import run_production_inference, get_model_manager, resolve_state_name

def test_production_pipeline():
    print("==========================================================")
    print("RUNNING PHASE 9.5 LOCATION HONESTY & RELIABILITY TESTS")
    print("==========================================================")

    # 1. Startup Artifact & Compatibility Validation
    print("\n1. Validating Model Manager Startup...")
    mgr = get_model_manager()
    assert len(mgr.calibrators) == 12, f"Expected 12 calibrators, got {len(mgr.calibrators)}"
    print("[PASS] Model Manager loaded 12 official calibrators successfully.")

    # 2. Test Location Resolution & Honesty Metadata
    print("\n2. Auditing Location Honesty Metadata across 14 Test Locations...")
    test_locations = [
        ("Uttar Pradesh", "Uttar Pradesh", True),
        ("Meerut", "Uttar Pradesh", True),
        ("Lucknow", "Uttar Pradesh", True),
        ("Maharashtra", "Maharashtra", True),
        ("Mumbai", "Maharashtra", True),
        ("Rajasthan", "Rajasthan", True),
        ("Karnataka", "Karnataka", True),
        ("Kerala", "Kerala", True),
        ("Andhra Pradesh", "Karnataka", False),
        ("Bihar", "Uttar Pradesh", False),
        ("Delhi", "Uttar Pradesh", False),
        ("Tamil Nadu", "Kerala", False),
        ("Himachal Pradesh", "Punjab", False),
        ("Madhya Pradesh", "Maharashtra", False)
    ]

    for loc_in, expected_state, expected_direct in test_locations:
        res_st, is_direct, note = resolve_state_name(loc_in)
        assert res_st == expected_state, f"Location '{loc_in}' resolved to '{res_st}', expected '{expected_state}'"
        assert is_direct == expected_direct, f"Location '{loc_in}' expected is_direct={expected_direct}, got {is_direct}"
        print(f"  [PASS] Location '{loc_in}' -> State: '{res_st}' | Direct: {is_direct} | Note: {note}")

    # 3. Live Pipeline Forecast Metadata Validation
    print("\n3. Testing End-to-End Live Pipeline Honesty Metadata...")
    
    # Direct Match Test (Uttar Pradesh / Meerut)
    res_direct = run_production_inference(state="Uttar Pradesh", prediction_date_str="2024-06-15")
    assert res_direct['metadata']['is_direct_match'] == True
    assert "Direct validated Phase 3B model" in res_direct['metadata']['location_resolution_note']
    print(f"  [PASS] Direct Match (UP) -> Metadata: is_direct_match={res_direct['metadata']['is_direct_match']}")

    # Fallback Baseline Test (Andhra Pradesh -> Karnataka)
    res_fallback = run_production_inference(state="Andhra Pradesh", prediction_date_str="2024-06-15")
    assert res_fallback['metadata']['is_direct_match'] == False
    assert "Using regional baseline model (Karnataka)" in res_fallback['metadata']['location_resolution_note']
    print(f"  [PASS] Fallback Baseline (AP -> Karnataka) -> Metadata: is_direct_match={res_fallback['metadata']['is_direct_match']} | Note: {res_fallback['metadata']['location_resolution_note']}")

    print("\n==========================================================")
    print("ALL PHASE 9.5 LOCATION HONESTY TESTS PASSED (100%)!")
    print("==========================================================")

if __name__ == '__main__':
    test_production_pipeline()
