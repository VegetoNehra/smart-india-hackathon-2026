import os
import json
import joblib
import numpy as np
import pandas as pd

from xgboost import XGBClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (
    average_precision_score, roc_auc_score,
    precision_score, recall_score, f1_score,
    brier_score_loss
)

np.random.seed(42)

BASELINE_FEATURES = [
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

TEMPERATURE_FEATURES = [
    'climatological_temp_celsius',
    'climatological_temp_normal_celsius',
    'seasonal_temp_change_celsius'
]

FEATURE_SETS = {
    'Model_A_Baseline': BASELINE_FEATURES,
    'Model_B_Temperature_Enhanced': BASELINE_FEATURES + TEMPERATURE_FEATURES
}

TARGET_COLS = [
    'onset_7d', 'onset_14d', 'onset_21d', 'onset_30d',
    'break_7d', 'break_14d', 'break_21d', 'break_30d',
    'heavy_rain_7d', 'heavy_rain_14d', 'heavy_rain_21d', 'heavy_rain_30d'
]

def safe_pr_auc(y_true, y_prob):
    if len(np.unique(y_true)) < 2:
        return float(np.mean(y_true))
    return float(average_precision_score(y_true, y_prob))

def safe_roc_auc(y_true, y_prob):
    if len(np.unique(y_true)) < 2:
        return 0.5
    return float(roc_auc_score(y_true, y_prob))

def main():
    dataset_path = 'data/temperature/temperature_forecast_dataset.csv'
    models_dir = 'models/temperature_experiments'
    reports_dir = 'reports/phase5'

    os.makedirs(models_dir, exist_ok=True)
    os.makedirs(reports_dir, exist_ok=True)

    print("=== PHASE 5 TEMPERATURE MODELING EXPERIMENT ===")
    print("1. Loading Temperature-Enhanced Forecasting Dataset...")
    df = pd.read_csv(dataset_path)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').reset_index(drop=True)

    # Chronological Split (Train: 2022-2023, Val: 2024, Test: 2025)
    train_mask = df['date'] <= '2023-12-31'
    val_mask = (df['date'] >= '2024-01-01') & (df['date'] <= '2024-12-31')
    test_mask = df['date'] >= '2025-01-01'

    train_df = df[train_mask].copy()
    val_df = df[val_mask].copy()
    test_df = df[test_mask].copy()

    print(f"Dataset split complete:")
    print(f"  Train:      {len(train_df)} rows")
    print(f"  Validation: {len(val_df)} rows")
    print(f"  Test:       {len(test_df)} rows")

    experiment_metadata = {}
    summary_results = []

    print("\n2. Executing Baseline vs Temperature-Enhanced Controlled Experiment across 12 Targets...")

    for target in TARGET_COLS:
        print(f"\n==========================================")
        print(f"TARGET: {target}")
        print(f"==========================================")

        y_train = train_df[target].values
        y_val = val_df[target].values
        y_test = test_df[target].values

        n_pos = np.sum(y_train == 1)
        n_neg = np.sum(y_train == 0)
        scale_pos_weight = (n_neg / n_pos) if n_pos > 0 else 1.0

        target_metrics = {}

        for m_name, feat_list in FEATURE_SETS.items():
            X_tr = train_df[feat_list]
            X_v = val_df[feat_list]
            X_t = test_df[feat_list]

            # Train XGBoost
            model = XGBClassifier(
                n_estimators=100,
                max_depth=4,
                learning_rate=0.05,
                subsample=0.8,
                colsample_bytree=0.8,
                scale_pos_weight=scale_pos_weight,
                random_state=42,
                eval_metric='logloss',
                n_jobs=-1
            )
            model.fit(X_tr, y_train)

            # Calibrate on Validation
            cal = CalibratedClassifierCV(estimator=model, method='isotonic', cv='prefit')
            cal.fit(X_v, y_val)

            # Optimal F1 threshold on Validation
            val_probs = cal.predict_proba(X_v)[:, 1]
            best_thresh = 0.5
            best_val_f1 = -1.0
            for thresh in np.linspace(0.01, 0.99, 99):
                preds = (val_probs >= thresh).astype(int)
                f1 = f1_score(y_val, preds, zero_division=0)
                if f1 > best_val_f1:
                    best_val_f1 = f1
                    best_thresh = thresh

            # Evaluate on held-out Test set
            test_probs = cal.predict_proba(X_t)[:, 1]
            test_preds = (test_probs >= best_thresh).astype(int)

            pr_auc = safe_pr_auc(y_test, test_probs)
            roc_auc = safe_roc_auc(y_test, test_probs)
            brier = float(brier_score_loss(y_test, test_probs))
            prec = float(precision_score(y_test, test_preds, zero_division=0))
            rec = float(recall_score(y_test, test_preds, zero_division=0))
            f1 = float(f1_score(y_test, test_preds, zero_division=0))

            target_metrics[m_name] = {
                'num_features': len(feat_list),
                'pr_auc': pr_auc,
                'roc_auc': roc_auc,
                'brier_score': brier,
                'precision': prec,
                'recall': rec,
                'f1_score': f1,
                'optimal_threshold': float(best_thresh)
            }

            # Save Model B (Temperature-Enhanced) artifact
            if m_name == 'Model_B_Temperature_Enhanced':
                joblib.dump(model, os.path.join(models_dir, f"temperature_{target}.joblib"))
                joblib.dump(cal, os.path.join(models_dir, f"temperature_{target}_calibrator.joblib"))

                imps = dict(zip(feat_list, model.feature_importances_.astype(float)))
                target_metrics[m_name]['feature_importances'] = imps

        pr_a = target_metrics['Model_A_Baseline']['pr_auc']
        pr_b = target_metrics['Model_B_Temperature_Enhanced']['pr_auc']
        gain = pr_b - pr_a
        pct_gain = (gain / (pr_a + 1e-5)) * 100.0

        print(f"PR-AUC Comparison:")
        print(f"  Model A (Baseline):            {pr_a:.4f}")
        print(f"  Model B (Temp-Enhanced):       {pr_b:.4f} (Diff: {gain:+.4f} | {pct_gain:+.2f}%)")

        summary_results.append({
            'Target': target,
            'Model_A_Baseline_PR': pr_a,
            'Model_B_Temp_Enhanced_PR': pr_b,
            'Absolute_Temp_Gain': gain,
            'Relative_Gain_%': pct_gain,
            'Verdict': 'Meaningful Benefit' if gain > 0.02 else ('Limited Benefit' if gain > 0.001 else 'No Benefit')
        })

        experiment_metadata[target] = target_metrics

    # Save metadata JSON
    meta_json_path = os.path.join(models_dir, 'temperature_experiment_metadata.json')
    with open(meta_json_path, 'w') as f:
        json.dump(experiment_metadata, f, indent=2)
    print(f"\nExported complete temperature experiment metadata -> {meta_json_path}")

    summary_df = pd.DataFrame(summary_results)
    print("\n==================================================================================")
    print("TEMPERATURE MODEL EXPERIMENT SUMMARY (TEST SET 2025)")
    print("==================================================================================")
    print(summary_df.to_string(index=False))

if __name__ == '__main__':
    main()
