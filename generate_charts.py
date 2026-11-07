import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os

# Set style
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
fig_dir = r"c:\Users\LENOVO\OneDrive\SMART INDIA HACKATHON\report_assets"
os.makedirs(fig_dir, exist_ok=True)

# -------------------------------------------------------------
# Chart 1: System Architecture Diagram
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
ax.axis('off')

boxes = [
    {"title": "React Dashboard (Vite Frontend)\nGlassmorphism UI | Probability Curves", "x": 0.5, "y": 0.88, "w": 0.8, "h": 0.16, "color": "#1E293B", "tcolor": "#38BDF8"},
    {"title": "FastAPI Asynchronous REST Router\n(/api/v1/forecast/predict & /health)", "x": 0.5, "y": 0.64, "w": 0.8, "h": 0.16, "color": "#0F172A", "tcolor": "#34D399"},
    {"title": "Production Inference Pipeline\n30 Feature Extraction | Location Resolution", "x": 0.5, "y": 0.40, "w": 0.8, "h": 0.16, "color": "#1E1E38", "tcolor": "#F472B6"},
    {"title": "12 Frozen XGBoost Models\n+ Isotonic Calibrators (7D-30D)", "x": 0.26, "y": 0.12, "w": 0.4, "h": 0.18, "color": "#312E81", "tcolor": "#A78BFA"},
    {"title": "Phase 6 Advisory Engine\n5-Tier Rule Hierarchy | Crop Matrix", "x": 0.74, "y": 0.12, "w": 0.4, "h": 0.18, "color": "#064E3B", "tcolor": "#6EE7B7"}
]

for b in boxes:
    rect = mpatches.FancyBboxPatch((b["x"] - b["w"]/2, b["y"] - b["h"]/2), b["w"], b["h"], 
                                   facecolor=b["color"], edgecolor=b["tcolor"], linewidth=2, zorder=2, boxstyle="round,pad=0.02")
    ax.add_patch(rect)
    ax.text(b["x"], b["y"], b["title"], color="white", fontsize=10, fontweight="bold", ha="center", va="center", zorder=3)

# Connectors
arrows = [
    ((0.5, 0.80), (0.5, 0.72)),
    ((0.5, 0.56), (0.5, 0.48)),
    ((0.4, 0.32), (0.26, 0.21)),
    ((0.6, 0.32), (0.74, 0.21))
]

for start, end in arrows:
    ax.annotate("", xy=end, xytext=start,
                arrowprops=dict(arrowstyle="->", color="#38BDF8", lw=2.5), zorder=4)

plt.title("Monsoon Forecasting & Agricultural Advisory System Architecture", fontsize=13, fontweight="bold", pad=12, color="#0F172A")
plt.tight_layout()
plt.savefig(os.path.join(fig_dir, "chart_architecture.png"), bbox_inches="tight", dpi=300)
plt.close()

# -------------------------------------------------------------
# Chart 2: Model Performance Metrics (ROC-AUC & PR-AUC)
# -------------------------------------------------------------
horizons = ['7 Days', '14 Days', '21 Days', '30 Days']
onset_roc = [0.935, 0.957, 0.958, 0.969]
break_roc = [0.931, 0.939, 0.950, 0.964]
heavy_roc = [0.706, 0.704, 0.697, 0.702]

x = np.arange(len(horizons))
width = 0.25

fig, ax = plt.subplots(figsize=(9, 4.5), dpi=300)
rects1 = ax.bar(x - width, onset_roc, width, label='Monsoon Onset', color='#2563EB')
rects2 = ax.bar(x, break_roc, width, label='Break Spell', color='#D97706')
rects3 = ax.bar(x + width, heavy_roc, width, label='Heavy Rain', color='#DC2626')

ax.set_ylabel('Calibrated ROC-AUC Score', fontsize=11, fontweight='bold')
ax.set_title('Model Discriminative Performance (ROC-AUC) Across Lead Horizons', fontsize=12, fontweight='bold', pad=12)
ax.set_xticks(x)
ax.set_xticklabels(horizons, fontsize=10, fontweight='bold')
ax.set_ylim(0.5, 1.05)
ax.legend(frameon=True, facecolor='white', framealpha=0.9, fontsize=10)

for rects in [rects1, rects2, rects3]:
    for rect in rects:
        height = rect.get_height()
        ax.annotate(f'{height:.2f}',
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=8, fontweight='bold')

plt.tight_layout()
plt.savefig(os.path.join(fig_dir, "chart_roc_auc.png"), bbox_inches="tight", dpi=300)
plt.close()

# -------------------------------------------------------------
# Chart 3: Isotonic Calibration Error Reduction (Brier Score)
# -------------------------------------------------------------
models_label = ['Onset 7D', 'Onset 14D', 'Break 7D', 'Break 14D', 'Heavy 7D', 'Heavy 14D']
baseline_brier = [0.0205, 0.0401, 0.1757, 0.2093, 0.0338, 0.0582]
raw_xgb_brier = [0.0405, 0.0632, 0.0965, 0.0798, 0.0822, 0.1063]
calib_brier = [0.0180, 0.0302, 0.0863, 0.0743, 0.0336, 0.0602]

x = np.arange(len(models_label))
width = 0.25

fig, ax = plt.subplots(figsize=(9, 4.5), dpi=300)
ax.bar(x - width, raw_xgb_brier, width, label='Raw XGBoost Brier (Uncalibrated)', color='#EF4444')
ax.bar(x, baseline_brier, width, label='Historical Baseline Brier', color='#9CA3AF')
ax.bar(x + width, calib_brier, width, label='Isotonic Calibrated Brier (Production)', color='#10B981')

ax.set_ylabel('Brier Score (Lower is Better)', fontsize=11, fontweight='bold')
ax.set_title('Brier Score Improvement via Isotonic Calibration (Held-Out Test Set)', fontsize=12, fontweight='bold', pad=12)
ax.set_xticks(x)
ax.set_xticklabels(models_label, fontsize=10, fontweight='bold')
ax.legend(frameon=True, facecolor='white', framealpha=0.9, fontsize=10)

plt.tight_layout()
plt.savefig(os.path.join(fig_dir, "chart_brier_calibration.png"), bbox_inches="tight", dpi=300)
plt.close()

# -------------------------------------------------------------
# Chart 4: Top Feature Importance Profile
# -------------------------------------------------------------
features = [
    'cos_day_of_year',
    'doy (Day of Year)',
    'month',
    'rainfall_14d_sum',
    'IOD_Index',
    'consecutive_dry_days',
    'phase (MJO)',
    'RMM1 (MJO)',
    'Nino 3.4 SST Anomaly',
    'rainfall_30d_mean'
]
importance = [0.28, 0.16, 0.12, 0.09, 0.06, 0.05, 0.04, 0.04, 0.03, 0.03]

fig, ax = plt.subplots(figsize=(8, 4.5), dpi=300)
y_pos = np.arange(len(features))
ax.barh(y_pos, importance, align='center', color='#8B5CF6')
ax.set_yticks(y_pos)
ax.set_yticklabels(features, fontsize=10, fontweight='bold')
ax.invert_yaxis()
ax.set_xlabel('Relative Feature Importance Weight', fontsize=11, fontweight='bold')
ax.set_title('Top Meteorological & Teleconnection Features Driving Forecasts', fontsize=12, fontweight='bold', pad=12)

for i, v in enumerate(importance):
    ax.text(v + 0.005, i, f"{v*100:.0f}%", va='center', fontweight='bold', fontsize=9, color='#4C1D95')

ax.set_xlim(0, 0.32)
plt.tight_layout()
plt.savefig(os.path.join(fig_dir, "chart_feature_importance.png"), bbox_inches="tight", dpi=300)
plt.close()

# -------------------------------------------------------------
# Chart 5: Phase 6 Decision Priority Flowchart
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(9, 4.5), dpi=300)
ax.axis('off')

priorities = [
    {"p": "P1", "title": "False-Onset Risk Warning", "condition": "Onset 14D >= 60% AND Break 14D >= 50%", "color": "#7F1D1D", "border": "#EF4444"},
    {"p": "P2", "title": "Heavy Rain Threat Alert", "condition": "Heavy Rain Max >= 60%", "color": "#991B1B", "border": "#F87171"},
    {"p": "P3", "title": "Break Spell (Dry Spell) Warning", "condition": "Break Spell Max >= 60%", "color": "#9A3412", "border": "#F97316"},
    {"p": "P4", "title": "Monsoon Onset Favorable Alert", "condition": "Monsoon Onset Max >= 60%", "color": "#065F46", "border": "#10B981"},
    {"p": "P5", "title": "Normal Seasonal Operations", "condition": "All Event Probabilities < 60%", "color": "#1E293B", "border": "#64748B"}
]

y_starts = [0.82, 0.64, 0.46, 0.28, 0.10]
for i, item in enumerate(priorities):
    y = y_starts[i]
    rect_p = mpatches.FancyBboxPatch((0.05, y - 0.06), 0.12, 0.12, facecolor=item["color"], edgecolor=item["border"], linewidth=2, zorder=2, boxstyle="round,pad=0.01")
    ax.add_patch(rect_p)
    ax.text(0.11, y, item["p"], color="white", fontsize=11, fontweight="bold", ha="center", va="center", zorder=3)
    
    rect_d = mpatches.FancyBboxPatch((0.20, y - 0.06), 0.75, 0.12, facecolor="#F8FAFC", edgecolor=item["border"], linewidth=1.5, zorder=2, boxstyle="round,pad=0.01")
    ax.add_patch(rect_d)
    ax.text(0.22, y + 0.025, item["title"], color="#0F172A", fontsize=10, fontweight="bold", ha="left", va="center", zorder=3)
    ax.text(0.22, y - 0.025, f"Condition: {item['condition']}", color="#475569", fontsize=9, ha="left", va="center", zorder=3)

plt.title("Phase 6 Advisory Engine Priority Hierarchy", fontsize=12, fontweight="bold", pad=10, color="#0F172A")
plt.tight_layout()
plt.savefig(os.path.join(fig_dir, "chart_rule_hierarchy.png"), bbox_inches="tight", dpi=300)
plt.close()

# -------------------------------------------------------------
# Chart 6: Supported Crop Categories & Growth Stage Coverage
# -------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5), dpi=300)

categories = ['Cereals', 'Pulses', 'Oilseeds', 'Fiber', 'Horticulture', 'Sugarcane', 'Coarse Grains']
cat_counts = [25, 20, 18, 12, 15, 5, 10]
colors_cat = ['#3B82F6', '#10B981', '#F59E0B', '#EC4899', '#8B5CF6', '#14B8A6', '#6366F1']

ax1.pie(cat_counts, labels=categories, autopct='%1.1f%%', startangle=140, colors=colors_cat, 
        textprops={'fontsize': 8.5, 'weight': 'bold'})
ax1.set_title('Crop Categories Distribution (50+ Crops)', fontsize=11, fontweight='bold', pad=10)

stages = ['Sowing', 'Establishment', 'Vegetative', 'Flowering', 'Grain/Fruit', 'Harvest']
stage_coverage = [100, 100, 100, 100, 100, 100]
ax2.bar(stages, stage_coverage, color='#0D9488', width=0.55)
ax2.set_ylabel('Advisory Engine Coverage (%)', fontsize=10, fontweight='bold')
ax2.set_title('Growth Stage Sensitivity Coverage Across All Crops', fontsize=11, fontweight='bold', pad=10)
ax2.set_ylim(0, 125)
for i, v in enumerate(stage_coverage):
    ax2.text(i, v + 3, f"{v}%", ha='center', fontweight='bold', fontsize=9, color='#0F766E')
ax2.tick_params(axis='x', rotation=25)

plt.tight_layout()
plt.savefig(os.path.join(fig_dir, "chart_crop_stage_coverage.png"), bbox_inches="tight", dpi=300)
plt.close()

print("All 6 high-resolution charts generated successfully in report_assets directory!")
