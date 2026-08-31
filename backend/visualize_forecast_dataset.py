import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_forecast_visualizations():
    df_path = 'data/forecast_training_dataset.csv'
    output_dir = 'data/forecast_visualizations'
    os.makedirs(output_dir, exist_ok=True)

    if not os.path.exists(df_path):
        print(f"Dataset {df_path} not found.")
        return

    df = pd.read_csv(df_path)
    df['date'] = pd.to_datetime(df['date'])

    # Also load daily raw events for complete ground truth rendering
    daily_raw = pd.read_csv('data/labeled_daily_events.csv')
    daily_raw['date'] = pd.to_datetime(daily_raw['date'])

    # Pick 3 interesting prediction dates (Onset period in Kerala, Heavy Rain in Maharashtra, Break spell in Rajasthan)
    case_studies = [
        {'state': 'Kerala', 'date': '2024-05-20', 'title': 'Kerala Onset Prediction Horizon Case Study (Prediction Date: May 20, 2024)'},
        {'state': 'Maharashtra', 'date': '2024-07-05', 'title': 'Maharashtra Heavy Rain Horizon Case Study (Prediction Date: July 5, 2024)'},
        {'state': 'Rajasthan', 'date': '2024-08-10', 'title': 'Rajasthan Break Spell Horizon Case Study (Prediction Date: Aug 10, 2024)'}
    ]

    for case in case_studies:
        state = case['state']
        pred_date = pd.to_datetime(case['date'])

        # Get prediction row
        pred_row = df[(df['state'] == state) & (df['date'] == pred_date)]
        if pred_row.empty:
            continue
        pred_row = pred_row.iloc[0]

        # Get daily series for window [T-30, T+30]
        start_dt = pred_date - pd.Timedelta(days=30)
        end_dt = pred_date + pd.Timedelta(days=30)

        sub_daily = daily_raw[(daily_raw['state'] == state) & 
                              (daily_raw['date'] >= start_dt) & 
                              (daily_raw['date'] <= end_dt)].sort_values('date')

        if len(sub_daily) == 0:
            continue

        fig, ax = plt.subplots(figsize=(12, 6))

        # Split past vs future
        past_df = sub_daily[sub_daily['date'] <= pred_date]
        future_df = sub_daily[sub_daily['date'] > pred_date]

        # Bar plots
        ax.bar(past_df['date'], past_df['rainfall'], color='#2b5c8f', width=0.8, label='Historical Rainfall (<= Date T)')
        ax.bar(future_df['date'], future_df['rainfall'], color='#7eb0d5', width=0.8, alpha=0.7, label='Future Observed Rainfall (> Date T)')

        # Highlight prediction date line
        ax.axvline(x=pred_date, color='red', linestyle='--', linewidth=2.5, label=f'Prediction Date T ({case["date"]})')

        # Highlight future horizon windows (7D, 14D, 21D, 30D)
        ax.axvspan(pred_date, pred_date + pd.Timedelta(days=7), color='yellow', alpha=0.15, label='7-Day Horizon')
        ax.axvspan(pred_date + pd.Timedelta(days=7), pred_date + pd.Timedelta(days=14), color='orange', alpha=0.12, label='14-Day Horizon')
        ax.axvspan(pred_date + pd.Timedelta(days=14), pred_date + pd.Timedelta(days=21), color='purple', alpha=0.08, label='21-Day Horizon')
        ax.axvspan(pred_date + pd.Timedelta(days=21), pred_date + pd.Timedelta(days=30), color='green', alpha=0.05, label='30-Day Horizon')

        # Scatter event markers on future dates if they occurred
        onset_dates = future_df[future_df['onset'] == 1]['date']
        break_dates = future_df[future_df['break_spell'] == 1]['date']
        heavy_dates = future_df[future_df['heavy_rain'] == 1]['date']

        if not onset_dates.empty:
            ax.scatter(onset_dates, [max(sub_daily['rainfall'])*0.9]*len(onset_dates), color='green', s=120, zorder=5, marker='^', label='Event: Onset Flag')
        if not heavy_dates.empty:
            ax.scatter(heavy_dates, [max(sub_daily['rainfall'])*0.8]*len(heavy_dates), color='crimson', s=120, zorder=5, marker='*', label='Event: Heavy Rain (>=64.5mm)')
        if not break_dates.empty:
            ax.scatter(break_dates, [2.0]*len(break_dates), color='darkorange', s=60, zorder=5, marker='o', label='Event: Break Spell Day')

        # Annotate targets derived for Date T
        target_text = (
            f"TARGET VALUES AT DATE T:\n"
            f"Onset: 7d={pred_row['onset_7d']}, 14d={pred_row['onset_14d']}, 21d={pred_row['onset_21d']}, 30d={pred_row['onset_30d']}\n"
            f"Break: 7d={pred_row['break_7d']}, 14d={pred_row['break_14d']}, 21d={pred_row['break_21d']}, 30d={pred_row['break_30d']}\n"
            f"Heavy Rain: 7d={pred_row['heavy_rain_7d']}, 14d={pred_row['heavy_rain_14d']}, 21d={pred_row['heavy_rain_21d']}, 30d={pred_row['heavy_rain_30d']}"
        )
        ax.text(0.02, 0.95, target_text, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))

        ax.set_title(case['title'], fontsize=13, fontweight='bold')
        ax.set_ylabel('Daily Rainfall (mm)', fontsize=11)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))
        plt.xticks(rotation=45)
        ax.legend(loc='upper right', fontsize=8)
        plt.tight_layout()

        out_fn = os.path.join(output_dir, f"forecast_timeline_{state.lower()}_{case['date']}.png")
        plt.savefig(out_fn, dpi=150)
        plt.close()
        print(f"Exported Timeline Visualization -> {out_fn}")

if __name__ == '__main__':
    generate_forecast_visualizations()
