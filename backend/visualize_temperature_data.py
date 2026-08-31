import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def generate_temperature_visualizations():
    kaggle_csv = r'C:\Users\LENOVO\.cache\kagglehub\datasets\venky73\temperatures-of-india\versions\1\temperatures.csv'
    meta_json_path = 'models/temperature_experiments/temperature_experiment_metadata.json'
    reports_dir = 'reports/phase5'
    os.makedirs(reports_dir, exist_ok=True)

    # 1. Historical All-India Temperature Trend Plot (1901-2017)
    if os.path.exists(kaggle_csv):
        df_raw = pd.read_csv(kaggle_csv)
        df_raw.columns = df_raw.columns.str.strip().str.upper()

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(df_raw['YEAR'], df_raw['ANNUAL'], color='crimson', linewidth=1.5, label='Annual Mean Temp (°C)')
        
        # 10-year rolling mean trendline
        df_raw['ROLLING_10Y'] = df_raw['ANNUAL'].rolling(10, min_periods=1).mean()
        ax.plot(df_raw['YEAR'], df_raw['ROLLING_10Y'], color='darkred', linewidth=3.0, label='10-Year Moving Avg Trend')

        ax.axvspan(2022, 2025, color='gray', alpha=0.3, label='2022-2025 Forecasting Dataset (Zero Overlap)')

        ax.set_title('All-India Historical Mean Temperature Trend (1901–2017)', fontsize=12, fontweight='bold')
        ax.set_xlabel('Year', fontsize=11)
        ax.set_ylabel('Mean Temperature (°C)', fontsize=11)
        ax.legend(fontsize=9, loc='upper left')
        ax.grid(True, alpha=0.3)

        out_trend = os.path.join(reports_dir, 'historical_temperature_trend.png')
        plt.tight_layout()
        plt.savefig(out_trend, dpi=150)
        plt.close()
        print(f"Exported Historical Temperature Trend Chart -> {out_trend}")

    # 2. PR-AUC Comparison: Baseline vs Temperature-Enhanced Models
    if os.path.exists(meta_json_path):
        with open(meta_json_path, 'r') as f:
            meta_dict = json.load(f)

        targets = list(meta_dict.keys())
        base_pr = [meta_dict[t]['Model_A_Baseline']['pr_auc'] for t in targets]
        temp_pr = [meta_dict[t]['Model_B_Temperature_Enhanced']['pr_auc'] for t in targets]

        fig, ax = plt.subplots(figsize=(12, 6))
        x = np.arange(len(targets))
        width = 0.35

        ax.bar(x - width/2, base_pr, width, label='Model A (Phase 3B Baseline)', color='steelblue')
        ax.bar(x + width/2, temp_pr, width, label='Model B (Temperature-Enhanced)', color='coral')

        ax.set_title('Test Set PR-AUC Comparison: Baseline vs Temperature-Enhanced Models', fontsize=12, fontweight='bold')
        ax.set_ylabel('PR-AUC (Test 2025)', fontsize=11)
        ax.set_xticks(x)
        ax.set_xticklabels(targets, rotation=60, ha='right', fontsize=8)
        ax.legend(fontsize=9, loc='upper right')
        ax.grid(True, alpha=0.3)

        out_comp = os.path.join(reports_dir, 'baseline_vs_temperature_prauc.png')
        plt.tight_layout()
        plt.savefig(out_comp, dpi=150)
        plt.close()
        print(f"Exported PR-AUC Comparison Chart -> {out_comp}")

if __name__ == '__main__':
    generate_temperature_visualizations()
