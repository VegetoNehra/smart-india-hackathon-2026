import os
import json
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from xgboost import XGBClassifier
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from sklearn.metrics import (
    precision_recall_curve, average_precision_score,
    roc_curve, roc_auc_score,
    precision_score, recall_score, f1_score,
    brier_score_loss, confusion_matrix
)

# Set random seed for reproducibility
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
    reports_dir = 'reports/phase3b'

    os.makedirs(models_dir, exist_ok=True)
    os.makedirs(reports_dir, exist_ok=True)

    print("1. Loading dataset...")
    df = pd.read_csv(dataset_path)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').reset_index(drop=True)

    # ---------------------------------------------------------
    # CHRONOLOGICAL TRAIN / VALIDATION / TEST SPLIT
    # Train: 2022-01-01 to 2023-12-31 (~51%)
    # Val:   2024-01-01 to 2024-12-31 (~25.6%)
    # Test:  2025-01-01 to 2025-12-01 (~23.4%)
    # ---------------------------------------------------------
    train_mask = df['date'] <= '2023-12-31'
    val_mask = (df['date'] >= '2024-01-01') & (df['date'] <= '2024-12-31')
    test_mask = df['date'] >= '2025-01-01'

    train_df = df[train_mask].copy()
    val_df = df[val_mask].copy()
    test_df = df[test_mask].copy()

    print(f"Dataset split complete:")
    print(f"  Train:      {len(train_df)} rows ({train_df['date'].min().strftime('%Y-%m-%d')} to {train_df['date'].max().strftime('%Y-%m-%d')})")
    print(f"  Validation: {len(val_df)} rows ({val_df['date'].min().strftime('%Y-%m-%d')} to {val_df['date'].max().strftime('%Y-%m-%d')})")
    print(f"  Test:       {len(test_df)} rows ({test_df['date'].min().strftime('%Y-%m-%d')} to {test_df['date'].max().strftime('%Y-%m-%d')})")

    X_train, X_val, X_test = train_df[FEATURE_COLS], val_df[FEATURE_COLS], test_df[FEATURE_COLS]

    all_metadata = {}
    eval_results = []

    print("\n2. Training and evaluating 12 probabilistic models...")

    for target in TARGET_COLS:
        print(f"\n==========================================")
        print(f"TARGET: {target}")
        print(f"==========================================")

        y_train = train_df[target].values
        y_val = val_df[target].values
        y_test = test_df[target].values

        train_pos_rate = np.mean(y_train)
        val_pos_rate = np.mean(y_val)
        test_pos_rate = np.mean(y_test)

        print(f"Positive Rates - Train: {train_pos_rate*100:.2f}%, Val: {val_pos_rate*100:.2f}%, Test: {test_pos_rate*100:.2f}%")

        # -----------------------------------------------------
        # BASELINES
        # -----------------------------------------------------
        # Baseline A: Always 0
        b_a_val_prob = np.zeros_like(y_val, dtype=float)
        b_a_test_prob = np.zeros_like(y_test, dtype=float)

        # Baseline B: Historical Base Rate (Train Mean)
        b_b_val_prob = np.full_like(y_val, train_pos_rate, dtype=float)
        b_b_test_prob = np.full_like(y_test, train_pos_rate, dtype=float)

        # Baseline C: Seasonal Base Rate (Month-specific Train Mean)
        seasonal_means = train_df.groupby('month')[target].mean().to_dict()
        b_c_val_prob = val_df['month'].map(seasonal_means).fillna(train_pos_rate).values
        b_c_test_prob = test_df['month'].map(seasonal_means).fillna(train_pos_rate).values

        # Baseline B metrics on test
        base_b_pr_auc = average_precision_score(y_test, b_b_test_prob) if len(np.unique(y_test)) > 1 else 0.0
        base_b_brier = brier_score_loss(y_test, b_b_test_prob)

        # Baseline C metrics on test
        base_c_pr_auc = average_precision_score(y_test, b_c_test_prob) if len(np.unique(y_test)) > 1 else 0.0
        base_c_brier = brier_score_loss(y_test, b_c_test_prob)

        # -----------------------------------------------------
        # PRIMARY MODEL: XGBOOST CLASSIFIER WITH CLASS WEIGHTS
        # -----------------------------------------------------
        n_pos = np.sum(y_train == 1)
        n_neg = np.sum(y_train == 0)
        scale_pos_weight = (n_neg / n_pos) if n_pos > 0 else 1.0

        xgb_model = XGBClassifier(
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
        xgb_model.fit(X_train, y_train)

        # Uncalibrated Raw Probabilities
        val_probs_raw = xgb_model.predict_proba(X_val)[:, 1]
        test_probs_raw = xgb_model.predict_proba(X_test)[:, 1]

        raw_val_brier = brier_score_loss(y_val, val_probs_raw)
        raw_test_pr_auc = average_precision_score(y_test, test_probs_raw)
        raw_test_roc_auc = roc_auc_score(y_test, test_probs_raw)
        raw_test_brier = brier_score_loss(y_test, test_probs_raw)

        # -----------------------------------------------------
        # PROBABILITY CALIBRATION (Fitted on Validation Set)
        # Compare Isotonic vs Sigmoid scaling
        # -----------------------------------------------------
        cal_iso = CalibratedClassifierCV(estimator=xgb_model, method='isotonic', cv='prefit')
        cal_iso.fit(X_val, y_val)
        val_probs_iso = cal_iso.predict_proba(X_val)[:, 1]
        brier_iso_val = brier_score_loss(y_val, val_probs_iso)

        cal_sig = CalibratedClassifierCV(estimator=xgb_model, method='sigmoid', cv='prefit')
        cal_sig.fit(X_val, y_val)
        val_probs_sig = cal_sig.predict_proba(X_val)[:, 1]
        brier_sig_val = brier_score_loss(y_val, val_probs_sig)

        if brier_iso_val <= brier_sig_val:
            best_calibrator = cal_iso
            best_cal_method = 'isotonic'
            val_probs_cal = val_probs_iso
        else:
            best_calibrator = cal_sig
            best_cal_method = 'sigmoid'
            val_probs_cal = val_probs_sig

        test_probs_cal = best_calibrator.predict_proba(X_test)[:, 1]

        cal_test_pr_auc = average_precision_score(y_test, test_probs_cal)
        cal_test_roc_auc = roc_auc_score(y_test, test_probs_cal)
        cal_test_brier = brier_score_loss(y_test, test_probs_cal)

        # -----------------------------------------------------
        # THRESHOLD SELECTION (Validation F1 Maximization)
        # -----------------------------------------------------
        best_thresh = 0.5
        best_val_f1 = -1.0
        for thresh in np.linspace(0.01, 0.99, 99):
            preds = (val_probs_cal >= thresh).astype(int)
            f1 = f1_score(y_val, preds, zero_division=0)
            if f1 > best_val_f1:
                best_val_f1 = f1
                best_thresh = thresh

        # Evaluate threshold on Test set
        test_preds = (test_probs_cal >= best_thresh).astype(int)
        test_prec = precision_score(y_test, test_preds, zero_division=0)
        test_rec = recall_score(y_test, test_preds, zero_division=0)
        test_f1 = f1_score(y_test, test_preds, zero_division=0)
        cm = confusion_matrix(y_test, test_preds).tolist()

        print(f"Results on Test Set (2025):")
        print(f"  Base B PR-AUC:   {base_b_pr_auc:.4f} | Brier: {base_b_brier:.4f}")
        print(f"  Base C PR-AUC:   {base_c_pr_auc:.4f} | Brier: {base_c_brier:.4f}")
        print(f"  Raw XGB PR-AUC:  {raw_test_pr_auc:.4f} | ROC-AUC: {raw_test_roc_auc:.4f} | Brier: {raw_test_brier:.4f}")
        print(f"  Calibrated XGB ({best_cal_method}): PR-AUC: {cal_test_pr_auc:.4f} | ROC-AUC: {cal_test_roc_auc:.4f} | Brier: {cal_test_brier:.4f}")
        print(f"  Optimal Thresh (from Val): {best_thresh:.2f} -> Prec: {test_prec:.4f}, Rec: {test_rec:.4f}, F1: {test_f1:.4f}")

        # -----------------------------------------------------
        # SAVE ARTIFACTS
        # -----------------------------------------------------
        model_filename = os.path.join(models_dir, f"{target}.joblib")
        calibrator_filename = os.path.join(models_dir, f"{target}_calibrator.joblib")
        joblib.dump(xgb_model, model_filename)
        joblib.dump(best_calibrator, calibrator_filename)

        # Extract Feature Importances
        importances = dict(zip(FEATURE_COLS, xgb_model.feature_importances_.astype(float)))

        metadata = {
            'target': target,
            'event_type': target.split('_')[0] if not target.startswith('heavy_rain') else 'heavy_rain',
            'horizon': target.split('_')[-1],
            'training_period': '2022-01-01 to 2023-12-31',
            'validation_period': '2024-01-01 to 2024-12-31',
            'test_period': '2025-01-01 to 2025-12-01',
            'num_train_samples': len(train_df),
            'num_val_samples': len(val_df),
            'num_test_samples': len(test_df),
            'scale_pos_weight': float(scale_pos_weight),
            'best_calibration_method': best_cal_method,
            'optimal_threshold': float(best_thresh),
            'feature_importances': importances,
            'test_metrics': {
                'baseline_b_pr_auc': float(base_b_pr_auc),
                'baseline_b_brier': float(base_b_brier),
                'baseline_c_pr_auc': float(base_c_pr_auc),
                'baseline_c_brier': float(base_c_brier),
                'raw_xgb_pr_auc': float(raw_test_pr_auc),
                'raw_xgb_roc_auc': float(raw_test_roc_auc),
                'raw_xgb_brier': float(raw_test_brier),
                'calibrated_pr_auc': float(cal_test_pr_auc),
                'calibrated_roc_auc': float(cal_test_roc_auc),
                'calibrated_brier': float(cal_test_brier),
                'precision': float(test_prec),
                'recall': float(test_rec),
                'f1_score': float(test_f1),
                'confusion_matrix': cm
            }
        }
        all_metadata[target] = metadata

        eval_results.append({
            'Target': target,
            'Event': metadata['event_type'],
            'Horizon': metadata['horizon'],
            'Base B PR-AUC': base_b_pr_auc,
            'Raw XGB PR-AUC': raw_test_pr_auc,
            'Cal XGB PR-AUC': cal_test_pr_auc,
            'Cal XGB ROC-AUC': cal_test_roc_auc,
            'Base B Brier': base_b_brier,
            'Cal XGB Brier': cal_test_brier,
            'Precision': test_prec,
            'Recall': test_rec,
            'F1': test_f1,
            'Thresh': best_thresh
        })

    # Save metadata JSON
    meta_json_path = os.path.join(models_dir, 'model_metadata.json')
    with open(meta_json_path, 'w') as f:
        json.dump(all_metadata, f, indent=2)
    print(f"\nExported complete model metadata -> {meta_json_path}")

    eval_df = pd.DataFrame(eval_results)
    print("\n==================================================================================")
    print("FINAL PHASE 3B MODEL EVALUATION SUMMARY (TEST SET 2025)")
    print("==================================================================================")
    print(eval_df.to_string(index=False))

    # ---------------------------------------------------------
    # VISUALIZATIONS GENERATION
    # ---------------------------------------------------------
    print("\n3. Generating Phase 3B Evaluation Visualizations...")

    # A. PR Curves for 7D models
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    events_7d = [('onset_7d', 'Monsoon Onset 7D'), ('break_7d', 'Break Spell 7D'), ('heavy_rain_7d', 'Heavy Rain 7D')]
    for ax, (tgt, title) in zip(axes, events_7d):
        y_t = test_df[tgt].values
        xgb_m = joblib.load(os.path.join(models_dir, f"{tgt}.joblib"))
        cal_m = joblib.load(os.path.join(models_dir, f"{tgt}_calibrator.joblib"))

        p_raw = xgb_m.predict_proba(X_test)[:, 1]
        p_cal = cal_m.predict_proba(X_test)[:, 1]

        prec_raw, rec_raw, _ = precision_recall_curve(y_t, p_raw)
        prec_cal, rec_cal, _ = precision_recall_curve(y_t, p_cal)

        ax.plot(rec_raw, prec_raw, label=f"Raw XGB (PR-AUC={average_precision_score(y_t, p_raw):.3f})", color='steelblue')
        ax.plot(rec_cal, prec_cal, label=f"Calibrated (PR-AUC={average_precision_score(y_t, p_cal):.3f})", color='crimson', linestyle='--')
        ax.axhline(y=np.mean(y_t), color='gray', linestyle=':', label=f"Base Rate ({np.mean(y_t):.3f})")

        ax.set_title(title, fontweight='bold')
        ax.set_xlabel('Recall')
        ax.set_ylabel('Precision')
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    pr_fig_path = os.path.join(reports_dir, 'pr_curves_7d.png')
    plt.savefig(pr_fig_path, dpi=150)
    plt.close()
    print(f"Saved PR Curves -> {pr_fig_path}")

    # B. Calibration Curves (Reliability Diagrams)
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    for ax, (tgt, title) in zip(axes, events_7d):
        y_t = test_df[tgt].values
        xgb_m = joblib.load(os.path.join(models_dir, f"{tgt}.joblib"))
        cal_m = joblib.load(os.path.join(models_dir, f"{tgt}_calibrator.joblib"))

        p_raw = xgb_m.predict_proba(X_test)[:, 1]
        p_cal = cal_m.predict_proba(X_test)[:, 1]

        prob_true_raw, prob_pred_raw = calibration_curve(y_t, p_raw, n_bins=8, strategy='uniform')
        prob_true_cal, prob_pred_cal = calibration_curve(y_t, p_cal, n_bins=8, strategy='uniform')

        ax.plot([0, 1], [0, 1], 'k:', label='Perfectly Calibrated')
        ax.plot(prob_pred_raw, prob_true_raw, 's-', label=f'Raw XGB (Brier={brier_score_loss(y_t, p_raw):.4f})', color='orange')
        ax.plot(prob_pred_cal, prob_true_cal, 'o-', label=f'Calibrated (Brier={brier_score_loss(y_t, p_cal):.4f})', color='forestgreen')

        ax.set_title(f"Reliability Diagram: {title}", fontweight='bold')
        ax.set_xlabel('Mean Predicted Probability')
        ax.set_ylabel('Fraction of Positives')
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    cal_fig_path = os.path.join(reports_dir, 'calibration_curves_7d.png')
    plt.savefig(cal_fig_path, dpi=150)
    plt.close()
    print(f"Saved Calibration Curves -> {cal_fig_path}")

    # C. Horizon PR-AUC Performance Trend
    fig, ax = plt.subplots(figsize=(9, 5))
    horizons = ['7d', '14d', '21d', '30d']
    x_h = [7, 14, 21, 30]

    for ev_type, color in [('onset', 'forestgreen'), ('break', 'darkorange'), ('heavy_rain', 'crimson')]:
        prauc_vals = [all_metadata[f"{ev_type}_{h}"]['test_metrics']['calibrated_pr_auc'] for h in horizons]
        ax.plot(x_h, prauc_vals, marker='o', linewidth=2.5, label=f"{ev_type.replace('_', ' ').title()}", color=color)

    ax.set_title('PR-AUC vs Forecast Horizon (7D to 30D)', fontsize=13, fontweight='bold')
    ax.set_xlabel('Forecast Horizon (Days)', fontsize=11)
    ax.set_ylabel('Test Set PR-AUC', fontsize=11)
    ax.set_xticks(x_h)
    ax.set_xticklabels(['7 Days', '14 Days', '21 Days', '30 Days'])
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    h_fig_path = os.path.join(reports_dir, 'horizon_prauc_trend.png')
    plt.savefig(h_fig_path, dpi=150)
    plt.close()
    print(f"Saved Horizon Trend Chart -> {h_fig_path}")

    # D. Feature Importances for 7D targets
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    for ax, (tgt, title) in zip(axes, events_7d):
        imps = all_metadata[tgt]['feature_importances']
        top10 = pd.Series(imps).sort_values(ascending=True).tail(10)

        ax.barh(top10.index, top10.values, color='teal')
        ax.set_title(f"Top 10 Features: {title}", fontweight='bold')
        ax.set_xlabel('XGBoost Feature Importance (Gain)')
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    fi_fig_path = os.path.join(reports_dir, 'feature_importance_7d.png')
    plt.savefig(fi_fig_path, dpi=150)
    plt.close()
    print(f"Saved Feature Importance Chart -> {fi_fig_path}")

if __name__ == '__main__':
    main()
