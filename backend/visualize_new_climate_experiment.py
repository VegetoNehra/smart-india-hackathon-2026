import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def generate_new_climate_visualizations():
    kaggle_csv = r'C:\Users\LENOVO\.cache\kagglehub\datasets\ankushnarwade\indian-climate-dataset-20242025\versions\1\Indian_Climate_Dataset_2024_2025.csv'
    meta_json_path = 'models/new_climate_experiments/new_climate_experiment_metadata.json'
    reports_dir = 'reports/phase5b'
    os.makedirs(reports_dir, exist_ok=True)

    # 1. Daily Multi-Variable Climate Time Series Chart (Lucknow, UP & Delhi 2024-2025)
    if os.path.exists(kaggle_csv):
        df_raw = pd.read_csv(kaggle_csv)
        df_raw['Date'] = pd.to_datetime(df_raw['Date'])
        up_df = df_raw[df_raw['State'] == 'Uttar Pradesh'].sort_values('Date')

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 7), sharex=True)

        ax1.plot(up_df['Date'], up_df['Temperature_Avg (℃)' if 'Temperature_Avg (℃)' in up_df.columns else 'Temperature_Avg (°C)'], color='firebrick', linewidth=1.5, label='Temperature Avg (°C)')
        ax1.set_title('Daily Climate Time Series — Lucknow, Uttar Pradesh (2024–2025)', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Temperature (°C)', fontsize=11)
        ax1.legend(loc='upper right', fontsize=9)
        ax1.grid(True, alpha=0.3)

        ax2.plot(up_df['Date'], up_df['Humidity (%)'], color='royalblue', linewidth=1.5, label='Relative Humidity (%)')
        ax2.set_xlabel('Date', fontsize=11)
        ax2.set_ylabel('Humidity (%)', fontsize=11)
        ax2.legend(loc='upper right', fontsize=9)
        ax2.grid(True, alpha=0.3)

        out_ts = os.path.join(reports_dir, 'daily_climate_timeseries.png')
        plt.tight_layout()
        plt.savefig(out_ts, dpi=150)
        plt.close()
        print(f"Exported Daily Climate Time Series Chart -> {out_ts}")

    # 2. PR-AUC Ablation Comparison across Variants A, B, C, D
    if os.path.exists(meta_json_path):
        with open(meta_json_path, 'r') as f:
            meta_dict = json.load(f)

        targets = list(meta_dict.keys())
        labels = [t.replace('_', ' ').title() for t in targets]

        var_a = [meta_dict[t]['Variant_A_Baseline']['pr_auc'] for t in targets]
        var_b = [meta_dict[t]['Variant_B_Temp_Humidity']['pr_auc'] for t in targets]
        var_c = [meta_dict[t]['Variant_C_Temp_Hum_Press_Wind']['pr_auc'] for t in targets]
        var_d = [meta_dict[t]['Variant_D_Full_New_Climate']['pr_auc'] for t in targets]

        fig, ax = plt.subplots(figsize=(13, 6))
        x = np.arange(len(targets))
        width = 0.2

        ax.bar(x - 1.5*width, var_a, width, label='Variant A (Baseline)', color='gray')
        ax.bar(x - 0.5*width, var_b, width, label='Variant B (Temp + Humidity)', color='steelblue')
        ax.bar(x + 0.5*width, var_c, width, label='Variant C (+ Press & Wind)', color='darkorange')
        ax.bar(x + 1.5*width, var_d, width, label='Variant D (Full New Climate)', color='crimson')

        ax.set_title('Phase 5B Ablation Study: Test Set PR-AUC across 4 Climate Feature Variants', fontsize=12, fontweight='bold')
        ax.set_ylabel('PR-AUC (Test 2025)', fontsize=11)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=9)
        ax.legend(fontsize=9, loc='upper right')
        ax.grid(True, alpha=0.3)

        out_comp = os.path.join(reports_dir, 'ablation_new_climate_prauc.png')
        plt.tight_layout()
        plt.savefig(out_comp, dpi=150)
        plt.close()
        print(f"Exported New Climate Ablation Chart -> {out_comp}")

if __name__ == '__main__':
    generate_new_climate_visualizations()
