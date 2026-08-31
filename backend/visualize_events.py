import os
import pandas as pd
import matplotlib
matplotlib.use('Agg') # Non-interactive backend
import matplotlib.pyplot as plt

def generate_visualizations():
    daily_path = 'data/labeled_daily_events.csv'
    if not os.path.exists(daily_path):
        print(f"File not found: {daily_path}")
        return

    df = pd.read_csv(daily_path)
    df['date'] = pd.to_datetime(df['date'])

    output_dir = 'data/event_visualizations'
    os.makedirs(output_dir, exist_ok=True)

    # Select representative states for visual audit
    sample_states = ['Kerala', 'Maharashtra', 'Assam', 'West Bengal']
    sample_year = 2024 # Use 2024 as a representative year

    print(f"Generating visual validation charts for year {sample_year}...")

    for state in sample_states:
        sub = df[(df['state'] == state) & (df['year'] == sample_year)].sort_values('date')
        if sub.empty:
            continue

        fig, ax = plt.subplots(figsize=(12, 5))

        # 1. Plot daily rainfall bars
        ax.bar(sub['date'], sub['rainfall'], color='#3b82f6', width=1.0, alpha=0.7, label='Daily Rainfall (mm)')

        # 2. Highlight Break Spells (shaded background)
        break_sub = sub[sub['break_spell'] == 1]
        if not break_sub.empty:
            for d in break_sub['date']:
                ax.axvspan(d - pd.Timedelta(days=0.5), d + pd.Timedelta(days=0.5), 
                           color='#fb923c', alpha=0.25, lw=0)
            # Add single dummy line for legend
            ax.plot([], [], color='#fb923c', alpha=0.5, linewidth=6, label='Break Spell (Dry)')

        # 3. Highlight Onset Date
        onset_sub = sub[sub['onset'] == 1]
        if not onset_sub.empty:
            for idx, row in onset_sub.iterrows():
                ax.axvline(row['date'], color='#10b981', linestyle='--', linewidth=2, 
                           label=f"Onset: {row['date'].strftime('%d %b')}")

        # 4. Highlight Heavy Rain events (red scatter points)
        heavy_sub = sub[sub['heavy_rain'] == 1]
        if not heavy_sub.empty:
            ax.scatter(heavy_sub['date'], heavy_sub['rainfall'], color='#ef4444', s=50, 
                       zorder=5, label='Heavy Rain (>=64.5mm)')

        ax.set_title(f"Monsoon Event Detection Audit — {state} ({sample_year})", fontsize=14, fontweight='bold', pad=12)
        ax.set_ylabel("Rainfall (mm/day)", fontsize=11)
        ax.set_xlabel("Date", fontsize=11)
        ax.grid(True, linestyle=':', alpha=0.5)
        ax.legend(loc='upper right', frameon=True)

        plt.tight_layout()
        fig_path = os.path.join(output_dir, f"event_audit_{state.lower().replace(' ', '_')}_{sample_year}.png")
        plt.savefig(fig_path, dpi=150)
        plt.close()
        print(f"Saved plot -> {fig_path}")

if __name__ == "__main__":
    generate_visualizations()
