import os
import glob
import numpy as np
import pandas as pd
from dataclasses import dataclass, asdict

@dataclass
class EventConfig:
    """
    Configurable initial hypotheses for event labeling.
    All thresholds can be easily revised after inspecting resulting event distributions.
    """
    # 1. Onset Hypotheses
    onset_window_start_doy: int = 130  # May 10
    onset_window_end_doy: int = 196    # July 15
    onset_daily_thresh_mm: float = 2.5 # Daily rain threshold (mm/day)
    onset_consecutive_days: int = 2    # Consecutive days required
    onset_cum_thresh_mm: float = 15.0  # 3-day cumulative threshold (mm)

    # 2. Break-Spell (Dry Spell) Hypotheses
    break_window_start_doy: int = 153  # June 1 (Active Monsoon start)
    break_window_end_doy: int = 273    # Sept 30 (Active Monsoon end)
    break_dry_thresh_mm: float = 1.0   # Daily dry threshold (mm/day)
    break_min_duration_days: int = 3   # Minimum consecutive days

    # 3. Heavy Rain Hypotheses
    heavy_rain_thresh_mm: float = 64.5 # IMD Heavy Rain Standard (mm/day)
    very_heavy_thresh_mm: float = 115.5 # IMD Very Heavy Rain (mm/day)
    extreme_heavy_thresh_mm: float = 204.4 # IMD Extremely Heavy Rain (mm/day)

# Representative coordinates for key monsoon monitoring regions in India
STATE_COORDINATES = {
    "Kerala": (10.8505, 76.2711),
    "Karnataka": (15.3173, 75.7139),
    "Maharashtra": (19.7515, 75.7139),
    "Gujarat": (22.2587, 71.1924),
    "Rajasthan": (27.0238, 74.2179),
    "Punjab": (31.1471, 75.3412),
    "Uttar Pradesh": (26.8467, 80.9462),
    "West Bengal": (22.9868, 87.8550),
    "Assam": (26.2006, 92.9376)
}

def load_grd_daily_series(filepath, lat, lng):
    """
    Parses binary 0.25 x 0.25 IMD gridded daily rainfall data (.grd).
    Grid specs: 135 columns (66.5E to 100.0E), 129 rows (6.5N to 38.5N), float32.
    """
    if not os.path.exists(filepath):
        return None

    # Derive year from filename (e.g. Rainfall_ind2022_rfp25.grd)
    filename = os.path.basename(filepath)
    year = int(''.join(filter(str.isdigit, filename))[:4])

    num_cols = 135
    num_rows = 129
    col_idx = int((lng - 66.5) / 0.25)
    row_idx = int((lat - 6.5) / 0.25)

    if col_idx < 0 or col_idx >= num_cols or row_idx < 0 or row_idx >= num_rows:
        return None

    day_bytes = num_cols * num_rows * 4
    file_size = os.path.getsize(filepath)
    num_days = file_size // day_bytes

    daily_rain = []
    with open(filepath, "rb") as f:
        for d in range(num_days):
            f.seek(d * day_bytes)
            day_grid = np.fromfile(f, dtype=np.float32, count=num_cols * num_rows)
            day_grid = day_grid.reshape((num_rows, num_cols))
            val = day_grid[row_idx, col_idx]
            # Replace negative missing values (-999.0) with 0.0
            daily_rain.append(float(val) if val >= 0 else 0.0)

    dates = pd.date_range(start=f"{year}-01-01", periods=num_days, freq='D')
    return pd.DataFrame({'date': dates, 'rainfall': daily_rain, 'year': year})

def detect_onset_daily(df_state, cfg: EventConfig):
    """
    Detects Monsoon Onset from daily rainfall observations.
    Persistence + cumulative threshold within window (May 10 - July 15).
    """
    df_state = df_state.sort_values('date').copy()
    df_state['doy'] = df_state['date'].dt.dayofyear
    df_state['onset'] = 0
    df_state['onset_date'] = None

    for yr in df_state['year'].unique():
        sub = df_state[df_state['year'] == yr]
        window = sub[(sub['doy'] >= cfg.onset_window_start_doy) & (sub['doy'] <= cfg.onset_window_end_doy)].copy()

        rain_vals = window['rainfall'].values
        dates = window['date'].values

        for i in range(len(rain_vals) - 2):
            r1, r2, r3 = rain_vals[i], rain_vals[i+1], rain_vals[i+2]
            if (r1 >= cfg.onset_daily_thresh_mm and 
                r2 >= cfg.onset_daily_thresh_mm and 
                (r1 + r2 + r3) >= cfg.onset_cum_thresh_mm):
                
                onset_dt = dates[i+1] # Onset declared on 2nd day of persistence
                df_state.loc[df_state['date'] == onset_dt, 'onset'] = 1
                df_state.loc[df_state['year'] == yr, 'onset_date'] = pd.to_datetime(onset_dt).strftime('%Y-%m-%d')
                break

    return df_state

def detect_breaks_daily(df_state, cfg: EventConfig):
    """
    Detects Break Spells (dry spells) during active monsoon (June 1 - Sept 30).
    Captures break flag and consecutive duration.
    """
    df_state = df_state.sort_values('date').copy()
    df_state['doy'] = df_state['date'].dt.dayofyear
    df_state['break_spell'] = 0
    df_state['break_duration'] = 0

    monsoon_mask = (df_state['doy'] >= cfg.break_window_start_doy) & (df_state['doy'] <= cfg.break_window_end_doy)

    dry_count = 0
    break_spell_arr = np.zeros(len(df_state), dtype=int)
    duration_arr = np.zeros(len(df_state), dtype=int)

    rain_vals = df_state['rainfall'].values
    m_mask = monsoon_mask.values

    for i in range(len(df_state)):
        if m_mask[i] and rain_vals[i] < cfg.break_dry_thresh_mm:
            dry_count += 1
            duration_arr[i] = dry_count
            if dry_count >= cfg.break_min_duration_days:
                break_spell_arr[i - dry_count + 1 : i + 1] = 1
        else:
            dry_count = 0

    df_state['break_spell'] = break_spell_arr
    df_state['break_duration'] = duration_arr
    return df_state

def detect_heavy_rain_daily(df_state, cfg: EventConfig):
    """
    Detects Heavy Rain events from daily rainfall observations.
    Categorizes intensity into Moderate, Heavy, Very Heavy, Extremely Heavy.
    """
    rain = df_state['rainfall']
    df_state['heavy_rain'] = (rain >= cfg.heavy_rain_thresh_mm).astype(int)

    # Classify intensity
    conditions = [
        rain < cfg.heavy_rain_thresh_mm,
        (rain >= cfg.heavy_rain_thresh_mm) & (rain < cfg.very_heavy_thresh_mm),
        (rain >= cfg.very_heavy_thresh_mm) & (rain < cfg.extreme_heavy_thresh_mm),
        rain >= cfg.extreme_heavy_thresh_mm
    ]
    choices = ['None/Moderate', 'Heavy', 'Very Heavy', 'Extremely Heavy']
    df_state['heavy_rain_class'] = np.select(conditions, choices, default='None/Moderate')
    return df_state

def process_daily_dataset(cfg: EventConfig):
    """
    Processes all available 0.25° x 0.25° IMD gridded daily data (2022-2025).
    """
    grd_files = sorted(glob.glob('data/Rainfall_ind*.grd'))
    print(f"Found {len(grd_files)} daily gridded binary files (.grd).")

    all_state_dfs = []
    for state, (lat, lng) in STATE_COORDINATES.items():
        state_series = []
        for filepath in grd_files:
            df = load_grd_daily_series(filepath, lat, lng)
            if df is not None:
                df['state'] = state
                df['region'] = f"{state}_Station"
                df['lat'] = lat
                df['lng'] = lng
                state_series.append(df)

        if state_series:
            combined_state = pd.concat(state_series, ignore_index=True)
            combined_state = detect_onset_daily(combined_state, cfg)
            combined_state = detect_breaks_daily(combined_state, cfg)
            combined_state = detect_heavy_rain_daily(combined_state, cfg)
            all_state_dfs.append(combined_state)

    if not all_state_dfs:
        print("No daily grid files found.")
        return None

    final_daily = pd.concat(all_state_dfs, ignore_index=True)
    cols_order = ['date', 'year', 'state', 'region', 'lat', 'lng', 'rainfall', 
                  'onset', 'onset_date', 'break_spell', 'break_duration', 
                  'heavy_rain', 'heavy_rain_class']
    final_daily = final_daily[cols_order]

    output_path = 'data/labeled_daily_events.csv'
    final_daily.to_csv(output_path, index=False)
    print(f"Exported Labeled Daily Dataset -> {output_path} ({len(final_daily)} records)")
    return final_daily

def process_monthly_historical_dataset():
    """
    Processes historical monthly subdivision rainfall data (1901-2015).
    CRITICAL: Does NOT fabricate daily onset/break events. Calculates monthly statistics only.
    """
    csv_path = 'data/rainfall in india 1901-2015.csv'
    if not os.path.exists(csv_path):
        print("Monthly historical dataset not found.")
        return None

    rain_raw = pd.read_csv(csv_path)
    rain_raw.columns = rain_raw.columns.str.strip().str.upper()

    month_cols = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
    rain_melted = rain_raw.melt(
        id_vars=['SUBDIVISION', 'YEAR'], 
        value_vars=month_cols,
        var_name='MONTH', 
        value_name='RAINFALL'
    )
    rain_melted['MONTH'] = rain_melted['MONTH'].str.upper()

    # Calculate monthly historical normals per subdivision & month
    normals = rain_melted.groupby(['SUBDIVISION', 'MONTH'])['RAINFALL'].mean().reset_index()
    normals = normals.rename(columns={'RAINFALL': 'MONTHLY_NORMAL'})

    monthly_stats = pd.merge(rain_melted, normals, on=['SUBDIVISION', 'MONTH'], how='left')
    monthly_stats['RAINFALL_ANOMALY_MM'] = monthly_stats['RAINFALL'] - monthly_stats['MONTHLY_NORMAL']
    monthly_stats['RAINFALL_PCT_OF_NORMAL'] = np.where(
        monthly_stats['MONTHLY_NORMAL'] > 0,
        (monthly_stats['RAINFALL'] / monthly_stats['MONTHLY_NORMAL']) * 100.0,
        100.0
    )

    monthly_stats = monthly_stats.rename(columns={
        'YEAR': 'year',
        'SUBDIVISION': 'subdivision',
        'MONTH': 'month',
        'RAINFALL': 'monthly_rainfall_mm',
        'MONTHLY_NORMAL': 'monthly_normal_mm',
        'RAINFALL_ANOMALY_MM': 'anomaly_mm',
        'RAINFALL_PCT_OF_NORMAL': 'pct_of_normal'
    })

    output_path = 'data/historical_monthly_stats.csv'
    monthly_stats.to_csv(output_path, index=False)
    print(f"Exported Historical Monthly Statistics -> {output_path} ({len(monthly_stats)} records)")
    return monthly_stats

if __name__ == "__main__":
    cfg = EventConfig()
    print("=== PHASE 2: EVENT LABELING PIPELINE ===")
    print(f"Event Hypotheses Configuration: {asdict(cfg)}")

    print("\n1. Generating Daily Labeled Event Dataset (2022-2025)...")
    daily_df = process_daily_dataset(cfg)

    print("\n2. Generating Historical Monthly Statistics (1901-2015)...")
    monthly_df = process_monthly_historical_dataset()

    if daily_df is not None:
        print("\n=== DAILY EVENT STATISTICS SUMMARY ===")
        print(f"Total Daily Observations: {len(daily_df)}")
        print(f"Total Onset Flag Days: {daily_df['onset'].sum()} ({daily_df['onset'].mean()*100:.2f}%)")
        print(f"Total Break Spell Days: {daily_df['break_spell'].sum()} ({daily_df['break_spell'].mean()*100:.2f}%)")
        print(f"Total Heavy Rain Days (>= 64.5mm): {daily_df['heavy_rain'].sum()} ({daily_df['heavy_rain'].mean()*100:.2f}%)")

        print("\n--- DAILY EVENT BREAKDOWN BY STATE ---")
        summary = daily_df.groupby('state').agg(
            Total_Days=('rainfall', 'count'),
            Years_Covered=('year', 'nunique'),
            Onset_Events=('onset', 'sum'),
            Break_Days=('break_spell', 'sum'),
            Heavy_Rain_Days=('heavy_rain', 'sum')
        ).reset_index()
        print(summary.to_string(index=False))
