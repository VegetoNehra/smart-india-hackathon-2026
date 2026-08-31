import os
import json
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.metrics import (
    average_precision_score, roc_auc_score,
    precision_score, recall_score, f1_score,
    brier_score_loss, confusion_matrix
)
from sklearn.calibration import calibration_curve

np.random.seed(42)

FEATURE_COLS = [
    'rainfall_today',
    'rainfall_3d_sum', 'rainfall_7d_sum', 'rainfall_14d_sum', 'rainfall_30d_sum',
    'rainfall_3d_mean', 'rainfall_7d_mean', 'rainfall_14d_mean', 'rainfall_30d_mean',
    'rainfall_7d_max', 'rainfall_14d_max', 'rainfall_30d_max',
    'consecutive_dry_days', 'consecutive_rain_days',
    'rainfall_7d_vs_previous_7d', 'rainfall_14d_vs_previous_14d', 'rainfall_trend',
    'month', 'doy', 'sin_day_of_year', 'cos_day_of_year',
    'Nino 3.4 SST Anomaly', 'SOI', 'ONI', 'RONI', 'IOD_Index',
    'RMM1', 'RMM2', 'amplitude', 'phase'
]

TARGET_COLS = [
    'onset_7d', 'onset_14d', 'onset_21d', 'onset_30d',
    'break_7d', 'break_14d', 'break_21d', 'break_30d',
    'heavy_rain_7d', 'heavy_rain_14d', 'heavy_rain_21d', 'heavy_rain_30d'
]

def main():
    dataset_path = 'data/forecast_training_dataset.csv'
    models_dir = 'models/event_models'
    reports_dir = 'reports/phase3b5'
    os.makedirs(reports_dir, exist_ok=True)

    print("=== PHASE 3B.5 MODEL & PROBABILITY INTEGRITY AUDIT ===")
    
    print("\n1. Loading forecasting dataset...")
    df = pd.read_csv(dataset_path)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').reset_index(drop=True)

    # ---------------------------------------------------------
    # 2. TEMPORAL SPLIT AUDIT
    # ---------------------------------------------------------
    train_mask = df['date'] <= '2023-12-31'
    val_mask = (df['date'] >= '2024-01-01') & (df['date'] <= '2024-12-31')
    test_mask = df['date'] >= '2025-01-01'

    train_df = df[train_mask].copy()
    val_df = df[val_mask].copy()
    test_df = df[test_mask].copy()

    print("\n[TEMPORAL SPLIT VERIFICATION]")
    print(f"Train:      {train_df['date'].min().strftime('%Y-%m-%d')} to {train_df['date'].max().strftime('%Y-%m-%d')} | Rows: {len(train_df)}")
    print(f"Validation: {val_df['date'].min().strftime('%Y-%m-%d')} to {val_df['date'].max().strftime('%Y-%m-%d')} | Rows: {len(val_df)}")
    print(f"Test:       {test_df['date'].min().strftime('%Y-%m-%d')} to {test_df['date'].max().strftime('%Y-%m-%d')} | Rows: {len(test_df)}")

    # Check date overlap
    assert train_df['date'].max() < val_df['date'].min(), "Train/Val temporal overlap detected!"
    assert val_df['date'].max() < test_df['date'].min(), "Val/Test temporal overlap detected!"
    print("[PASS] Strict chronological sequence verified (Train < Val < Test, zero overlap).")

    # ---------------------------------------------------------
    # 3. TARGET MONOTONICITY AUDIT
    # ---------------------------------------------------------
    print("\n[TARGET MONOTONICITY VERIFICATION]")
    mono_violations = 0
    for event in ['onset', 'break', 'heavy_rain']:
        v1 = (df[f'{event}_7d'] > df[f'{event}_14d']).sum()
        v2 = (df[f'{event}_14d'] > df[f'{event}_21d']).sum()
        v3 = (df[f'{event}_21d'] > df[f'{event}_30d']).sum()
        mono_violations += (v1 + v2 + v3)

    if mono_violations == 0:
        print("[PASS] Target Monotonicity verified across 100% of dataset (Target_7d <= Target_14d <= Target_21d <= Target_30d).")
    else:
        print(f"[FAIL] {mono_violations} monotonicity violations detected!")

    # ---------------------------------------------------------
    # 4. CLASS WEIGHT AUDIT (scale_pos_weight)
    # ---------------------------------------------------------
    print("\n[CLASS WEIGHT ISOLATION AUDIT]")
    weight_audit = []
    for target in TARGET_COLS:
        y_tr = train_df[target].values
        n_pos = np.sum(y_tr == 1)
        n_neg = np.sum(y_tr == 0)
        expected_weight = n_neg / n_pos
        weight_audit.append({'Target': target, 'Train_Positives': n_pos, 'Train_Negatives': n_neg, 'Scale_Pos_Weight': float(expected_weight)})
    
    weight_df = pd.DataFrame(weight_audit)
    print(weight_df.to_string(index=False))

    # ---------------------------------------------------------
    # 5. REPRODUCE METRICS & CALIBRATION AUDIT ON HELD-OUT TEST
    # ---------------------------------------------------------
    print("\n[METRIC REPRODUCTION & CALIBRATION VERIFICATION ON TEST SET (2025)]")
    X_test = test_df[FEATURE_COLS]
    meta_json_path = os.path.join(models_dir, 'model_metadata.json')
    with open(meta_json_path, 'r') as f:
        meta_dict = json.load(f)

    repro_results = []
    test_predictions = {}

    for target in TARGET_COLS:
        xgb_m = joblib.load(os.path.join(models_dir, f"{target}.joblib"))
        cal_m = joblib.load(os.path.join(models_dir, f"{target}_calibrator.joblib"))

        y_test = test_df[target].values
        p_raw = xgb_m.predict_proba(X_test)[:, 1]
        p_cal = cal_m.predict_proba(X_test)[:, 1]

        # Saved threshold in metadata
        thresh = meta_dict[target]['optimal_threshold']
        preds = (p_cal >= thresh).astype(int)

        pr_auc = average_precision_score(y_test, p_cal)
        roc_auc = roc_auc_score(y_test, p_cal)
        brier = brier_score_loss(y_test, p_cal)
        prec = precision_score(y_test, preds, zero_division=0)
        rec = recall_score(y_test, preds, zero_division=0)
        f1 = f1_score(y_test, preds, zero_division=0)

        rep_pr = meta_dict[target]['test_metrics']['calibrated_pr_auc']
        rep_brier = meta_dict[target]['test_metrics']['calibrated_brier']

        pr_diff = abs(pr_auc - rep_pr)
        brier_diff = abs(brier - rep_brier)

        status = "PASS" if (pr_diff < 1e-4 and brier_diff < 1e-4) else "DISCREPANCY"
        
        repro_results.append({
            'Target': target,
            'Rep_PR_AUC': rep_pr,
            'Audit_PR_AUC': pr_auc,
            'Rep_Brier': rep_brier,
            'Audit_Brier': brier,
            'ROC_AUC': roc_auc,
            'Precision': prec,
            'Recall': rec,
            'F1': f1,
            'Thresh': thresh,
            'Status': status
        })

        test_predictions[target] = {
            'y_test': y_test,
            'p_raw': p_raw,
            'p_cal': p_cal,
            'preds': preds,
            'thresh': thresh
        }

    repro_df = pd.DataFrame(repro_results)
    print(repro_df[['Target', 'Rep_PR_AUC', 'Audit_PR_AUC', 'Rep_Brier', 'Audit_Brier', 'Status']].to_string(index=False))

    # ---------------------------------------------------------
    # 6. RELIABILITY TABLES (10 PROBABILITY BINS)
    # ---------------------------------------------------------
    print("\n[RELIABILITY BINNED TABLES (TEST SET 2025)]")
    bin_edges = np.linspace(0.0, 1.0, 11)
    bin_labels = [f"{int(bin_edges[i]*100)}-{int(bin_edges[i+1]*100)}%" for i in range(10)]

    reliability_tables = {}
    for target in ['onset_7d', 'break_7d', 'heavy_rain_7d', 'onset_30d', 'break_30d', 'heavy_rain_30d']:
        y_t = test_predictions[target]['y_test']
        p_c = test_predictions[target]['p_cal']

        bin_rows = []
        for i in range(10):
            low, high = bin_edges[i], bin_edges[i+1]
            if i == 9:
                mask = (p_c >= low) & (p_c <= high)
            else:
                mask = (p_c >= low) & (p_c < high)

            count = int(np.sum(mask))
            if count > 0:
                mean_pred = float(np.mean(p_c[mask]))
                obs_freq = float(np.mean(y_t[mask]))
            else:
                mean_pred = float((low + high) / 2.0)
                obs_freq = np.nan

            bin_rows.append({
                'Bin': bin_labels[i],
                'Sample_Count': count,
                'Predicted_Mean': f"{mean_pred*100:.2f}%" if not np.isnan(mean_pred) else "N/A",
                'Observed_Freq': f"{obs_freq*100:.2f}%" if not np.isnan(obs_freq) else "N/A",
                'Status': 'Stable' if count >= 30 else ('Sparse' if count > 0 else 'Empty')
            })

        reliability_tables[target] = pd.DataFrame(bin_rows)
        print(f"\n--- Reliability Table: {target} ---")
        print(reliability_tables[target].to_string(index=False))

    # ---------------------------------------------------------
    # 7. BOOTSTRAP UNCERTAINTY ESTIMATION (200 RESAMPLES)
    # ---------------------------------------------------------
    print("\n[BOOTSTRAP 95% CONFIDENCE INTERVALS (200 Resamples)]")
    bootstrap_results = []
    n_bootstraps = 200

    for target in TARGET_COLS:
        y_t = test_predictions[target]['y_test']
        p_c = test_predictions[target]['p_cal']
        thresh = test_predictions[target]['thresh']
        n_samples = len(y_t)

        boot_pr_auc = []
        boot_brier = []
        boot_f1 = []

        for b in range(n_bootstraps):
            indices = np.random.choice(n_samples, size=n_samples, replace=True)
            y_b = y_t[indices]
            p_b = p_c[indices]

            if np.sum(y_b) > 0:
                boot_pr_auc.append(float(average_precision_score(y_b, p_b)))
                boot_brier.append(float(brier_score_loss(y_b, p_b)))
                preds_b = (p_b >= thresh).astype(int)
                boot_f1.append(float(f1_score(y_b, preds_b, zero_division=0)))

        pr_ci_low, pr_ci_high = np.percentile(boot_pr_auc, [2.5, 97.5])
        brier_ci_low, brier_ci_high = np.percentile(boot_brier, [2.5, 97.5])
        f1_ci_low, f1_ci_high = np.percentile(boot_f1, [2.5, 97.5])

        pos_count = int(np.sum(y_t == 1))

        bootstrap_results.append({
            'Target': target,
            'Test_Positives': pos_count,
            'PR_AUC_Mean': float(np.mean(boot_pr_auc)),
            'PR_AUC_95_CI': f"[{pr_ci_low:.4f}, {pr_ci_high:.4f}]",
            'Brier_Mean': float(np.mean(boot_brier)),
            'Brier_95_CI': f"[{brier_ci_low:.4f}, {brier_ci_high:.4f}]",
            'F1_Mean': float(np.mean(boot_f1)),
            'F1_95_CI': f"[{f1_ci_low:.4f}, {f1_ci_high:.4f}]"
        })

    boot_df = pd.DataFrame(bootstrap_results)
    print(boot_df.to_string(index=False))

    # ---------------------------------------------------------
    # 8. SEASONAL BASELINE VS XGBOOST INCREMENTAL SKILL
    # ---------------------------------------------------------
    print("\n[SEASONAL BASELINE VS XGBOOST SKILL COMPARISON]")
    skill_rows = []
    for target in TARGET_COLS:
        base_c_pr = meta_dict[target]['test_metrics']['baseline_c_pr_auc']
        cal_xgb_pr = meta_dict[target]['test_metrics']['calibrated_pr_auc']
        
        gain_pr = cal_xgb_pr - base_c_pr
        pct_gain = (gain_pr / (base_c_pr + 1e-5)) * 100.0

        skill_rows.append({
            'Target': target,
            'Seasonal_Base_PR_AUC': base_c_pr,
            'XGB_Calibrated_PR_AUC': cal_xgb_pr,
            'Absolute_Gain': gain_pr,
            'Relative_Gain_Pct': pct_gain,
            'Verdict': 'High Skill' if gain_pr > 0.10 else ('Moderate Skill' if gain_pr > 0.02 else 'Marginal/Weak')
        })

    skill_df = pd.DataFrame(skill_rows)
    print(skill_df.to_string(index=False))

    # ---------------------------------------------------------
    # 9. PROBABILITY DISTRIBUTION AUDIT
    # ---------------------------------------------------------
    print("\n[PROBABILITY DISTRIBUTION AUDIT (TEST SET)]")
    dist_audit_rows = []
    for target in TARGET_COLS:
        p_c = test_predictions[target]['p_cal']
        dist_audit_rows.append({
            'Target': target,
            'Min_Prob': float(np.min(p_c)),
            'Q25': float(np.percentile(p_c, 25)),
            'Median': float(np.median(p_c)),
            'Q75': float(np.percentile(p_c, 75)),
            'Max_Prob': float(np.max(p_c)),
            'Mean_Prob': float(np.mean(p_c)),
            'Collapse_Check': 'PASS (Healthy spread)' if np.std(p_c) > 0.01 else 'FAIL (Probability Collapse)'
        })

    dist_audit_df = pd.DataFrame(dist_audit_rows)
    print(dist_audit_df.to_string(index=False))

    # Save summary data for report generation
    audit_summary_file = os.path.join(reports_dir, 'audit_summary_metrics.json')
    summary_export = {
        'weight_audit': weight_df.to_dict(orient='records'),
        'repro_audit': repro_df.to_dict(orient='records'),
        'bootstrap_audit': boot_df.to_dict(orient='records'),
        'skill_audit': skill_df.to_dict(orient='records'),
        'dist_audit': dist_audit_df.to_dict(orient='records'),
        'reliability_tables': {k: v.to_dict(orient='records') for k, v in reliability_tables.items()}
    }
    with open(audit_summary_file, 'w') as f:
        json.dump(summary_export, f, indent=2)
    print(f"\nExported complete audit summary JSON -> {audit_summary_file}")

if __name__ == '__main__':
    main()
