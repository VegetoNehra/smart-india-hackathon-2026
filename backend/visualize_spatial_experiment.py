import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def generate_spatial_experiment_visualizations():
    meta_json_path = 'models/spatial_experiments/spatial_experiment_metadata.json'
    reports_dir = 'reports/phase4b'
    os.makedirs(reports_dir, exist_ok=True)

    if not os.path.exists(meta_json_path):
        print(f"Metadata file {meta_json_path} not found.")
        return

    with open(meta_json_path, 'r') as f:
        meta_dict = json.load(f)

    # 1. Ablation Comparison Bar Chart for Break Spell Targets (where spatial features helped most!)
    fig, ax = plt.subplots(figsize=(10, 6))

    targets = ['break_7d', 'break_14d', 'break_21d', 'break_30d']
    labels = ['7-Day Break', '14-Day Break', '21-Day Break', '30-Day Break']

    var_a = [meta_dict[t]['Variant_A_Baseline']['pr_auc'] for t in targets]
    var_b = [meta_dict[t]['Variant_B_IDW_Rainfall']['pr_auc'] for t in targets]
    var_c = [meta_dict[t]['Variant_C_IDW_plus_Variability']['pr_auc'] for t in targets]
    var_d = [meta_dict[t]['Variant_D_Full_Spatial']['pr_auc'] for t in targets]

    x = np.arange(len(targets))
    width = 0.2

    ax.bar(x - 1.5*width, var_a, width, label='Variant A (Baseline)', color='gray')
    ax.bar(x - 0.5*width, var_b, width, label='Variant B (IDW Spatial)', color='steelblue')
    ax.bar(x + 0.5*width, var_c, width, label='Variant C (IDW + Grid Var)', color='forestgreen')
    ax.bar(x + 1.5*width, var_d, width, label='Variant D (Full Spatial)', color='darkred')

    ax.set_title('Ablation Study: PR-AUC across Feature Variants for Break Spells', fontsize=12, fontweight='bold')
    ax.set_ylabel('Test Set PR-AUC (2025)', fontsize=11)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=10)
    ax.legend(fontsize=9, loc='upper right')
    ax.grid(True, alpha=0.3)

    out_ablation = os.path.join(reports_dir, 'ablation_break_spells.png')
    plt.tight_layout()
    plt.savefig(out_ablation, dpi=150)
    plt.close()
    print(f"Exported Ablation Chart -> {out_ablation}")

    # 2. Feature Importance for Variant C (Break 21D where Variant C gained +13.85%)
    fig, ax = plt.subplots(figsize=(10, 6))
    imps = meta_dict['break_21d']['Variant_D_Full_Spatial']['feature_importances']
    top12 = pd.Series(imps).sort_values(ascending=True).tail(12)

    # Highlight spatial features in green vs climate in blue
    colors = ['forestgreen' if 'spatial' in k or 'grid' in k else 'navy' for k in top12.index]

    ax.barh(top12.index, top12.values, color=colors)
    ax.set_title('Top 12 Features for Break 21D (Full Spatial Model)', fontsize=12, fontweight='bold')
    ax.set_xlabel('XGBoost Feature Importance (Gain)', fontsize=11)
    ax.grid(True, alpha=0.3)

    # Custom legend
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], color='forestgreen', lw=4, label='Spatial / IDW Grid Feature'),
        Line2D([0], [0], color='navy', lw=4, label='Baseline / Climate Feature')
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=9)

    out_fi = os.path.join(reports_dir, 'spatial_feature_importance_break_21d.png')
    plt.tight_layout()
    plt.savefig(out_fi, dpi=150)
    plt.close()
    print(f"Exported Feature Importance Chart -> {out_fi}")

if __name__ == '__main__':
    generate_spatial_experiment_visualizations()
