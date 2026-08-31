import os
import numpy as np
import pandas as pd

def build_forecasting_dataset():
    daily_csv_path = 'data/labeled_daily_events.csv'
    climate_csv_path = 'data/climate_indices_merged.csv'
    output_path = 'data/forecast_training_dataset.csv'

    if not os.path.exists(daily_csv_path):
        raise FileNotFoundError(f"Daily labeled events dataset not found at {daily_csv_path}")
    if not os.path.exists(climate_csv_path):
        raise FileNotFoundError(f"Climate indices dataset not found at {climate_csv_path}")

    print("1. Loading source datasets...")
    df_daily = pd.read_csv(daily_csv_path)
    df_daily['date'] = pd.to_datetime(df_daily['date'])
    df_daily = df_daily.sort_values(['state', 'date']).reset_index(drop=True)

    df_climate = pd.read_csv(climate_csv_path)
    df_climate['Month'] = df_climate['Month'].str.upper()

    month_to_num = {'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6,
                    'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12}
    df_climate['month_num'] = df_climate['Month'].map(month_to_num)

    print("2. Constructing features and future target labels per state/region...")
    processed_dfs = []

    for (state, region), group in df_daily.groupby(['state', 'region']):
        group = group.sort_values('date').copy()
        
        # ----------------------------------------------------
        # FEATURE ENGINEERING (STRICTLY <= DATE T)
        # ----------------------------------------------------
        rain = group['rainfall'].values
        n_rows = len(group)

        # Basic lags / rolling windows (backward looking: T-k+1 to T)
        group['rainfall_today'] = rain
        group['rainfall_3d_sum'] = pd.Series(rain, index=group.index).rolling(3, min_periods=1).sum()
        group['rainfall_7d_sum'] = pd.Series(rain, index=group.index).rolling(7, min_periods=1).sum()
        group['rainfall_14d_sum'] = pd.Series(rain, index=group.index).rolling(14, min_periods=1).sum()
        group['rainfall_30d_sum'] = pd.Series(rain, index=group.index).rolling(30, min_periods=1).sum()

        group['rainfall_3d_mean'] = pd.Series(rain, index=group.index).rolling(3, min_periods=1).mean()
        group['rainfall_7d_mean'] = pd.Series(rain, index=group.index).rolling(7, min_periods=1).mean()
        group['rainfall_14d_mean'] = pd.Series(rain, index=group.index).rolling(14, min_periods=1).mean()
        group['rainfall_30d_mean'] = pd.Series(rain, index=group.index).rolling(30, min_periods=1).mean()

        group['rainfall_7d_max'] = pd.Series(rain, index=group.index).rolling(7, min_periods=1).max()
        group['rainfall_14d_max'] = pd.Series(rain, index=group.index).rolling(14, min_periods=1).max()
        group['rainfall_30d_max'] = pd.Series(rain, index=group.index).rolling(30, min_periods=1).max()

        # Consecutive dry / rain days computation strictly up to date T
        consec_dry = np.zeros(n_rows, dtype=int)
        consec_rain = np.zeros(n_rows, dtype=int)

        curr_dry = 0
        curr_rain = 0
        for i in range(n_rows):
            r_val = rain[i]
            if r_val < 1.0: # EventConfig.break_dry_thresh_mm
                curr_dry += 1
                curr_rain = 0
            else:
                curr_dry = 0

            if r_val >= 2.5: # EventConfig.onset_daily_thresh_mm
                curr_rain += 1
            else:
                curr_rain = 0

            consec_dry[i] = curr_dry
            consec_rain[i] = curr_rain

        group['consecutive_dry_days'] = consec_dry
        group['consecutive_rain_days'] = consec_rain

        # Rainfall trend features
        # Previous 7d sum (T-13 to T-7)
        prev_7d_sum = pd.Series(rain, index=group.index).shift(7).rolling(7, min_periods=1).sum().fillna(0.0)
        prev_14d_sum = pd.Series(rain, index=group.index).shift(14).rolling(14, min_periods=1).sum().fillna(0.0)

        group['rainfall_7d_vs_previous_7d'] = (group['rainfall_7d_sum'] - prev_7d_sum).fillna(0.0)
        group['rainfall_14d_vs_previous_14d'] = (group['rainfall_14d_sum'] - prev_14d_sum).fillna(0.0)
        group['rainfall_trend'] = ((group['rainfall_7d_sum'] - prev_7d_sum) / (group['rainfall_7d_sum'] + prev_7d_sum + 1e-5)).fillna(0.0)

        # Seasonal features
        group['doy'] = group['date'].dt.dayofyear
        group['month'] = group['date'].dt.month
        group['sin_day_of_year'] = np.sin(2 * np.pi * group['doy'] / 365.25)
        group['cos_day_of_year'] = np.cos(2 * np.pi * group['doy'] / 365.25)

        # ----------------------------------------------------
        # CLIMATE INDEX TEMPORAL ALIGNMENT (LAGGED 1 MONTH)
        # For date T in (Year Y, Month M), map climate from (Year Y_prev, Month M_prev)
        # where M_prev = M - 1 (or 12 if M == 1)
        # ----------------------------------------------------
        target_year = group['date'].dt.year.values
        target_month = group['date'].dt.month.values

        climate_year_lag = np.where(target_month == 1, target_year - 1, target_year)
        climate_month_lag = np.where(target_month == 1, 12, target_month - 1)

        group['climate_match_year'] = climate_year_lag
        group['climate_match_month'] = climate_month_lag

        # Merge climate features
        group = pd.merge(
            group,
            df_climate.rename(columns={'Year': 'climate_match_year', 'month_num': 'climate_match_month'}),
            on=['climate_match_year', 'climate_match_month'],
            how='left'
        )

        # Clean up merged auxiliary climate cols
        group = group.drop(columns=['Month', 'climate_match_year', 'climate_match_month'])

        # ----------------------------------------------------
        # TARGET CONSTRUCTION (LOOKAHEAD FUTURE WINDOW (T, T+N])
        # ----------------------------------------------------
        onset_arr = group['onset'].values
        break_arr = group['break_spell'].values
        heavy_arr = group['heavy_rain'].values

        for N in [7, 14, 21, 30]:
            onset_target = np.zeros(n_rows, dtype=float)
            break_target = np.zeros(n_rows, dtype=float)
            heavy_target = np.zeros(n_rows, dtype=float)

            for i in range(n_rows):
                if i + N >= n_rows:
                    # Incomplete future window near end of dataset -> NaN
                    onset_target[i] = np.nan
                    break_target[i] = np.nan
                    heavy_target[i] = np.nan
                else:
                    # Window strictly AFTER date T: [i+1, i+N] inclusive
                    onset_target[i] = 1.0 if np.any(onset_arr[i+1 : i+N+1] == 1) else 0.0
                    break_target[i] = 1.0 if np.any(break_arr[i+1 : i+N+1] == 1) else 0.0
                    heavy_target[i] = 1.0 if np.any(heavy_arr[i+1 : i+N+1] == 1) else 0.0

            group[f'onset_{N}d'] = onset_target
            group[f'break_{N}d'] = break_target
            group[f'heavy_rain_{N}d'] = heavy_target

        processed_dfs.append(group)

    final_df = pd.concat(processed_dfs, ignore_index=True)

    # Filter out rows with NaN targets (incomplete 30-day lookahead window at dataset boundary)
    valid_mask = final_df['onset_30d'].notna()
    final_df_valid = final_df[valid_mask].copy()

    # Convert targets to int
    target_cols = [f'{event}_{N}d' for event in ['onset', 'break', 'heavy_rain'] for N in [7, 14, 21, 30]]
    for col in target_cols:
        final_df_valid[col] = final_df_valid[col].astype(int)

    # ----------------------------------------------------
    # ORDER & FORMAT COLUMNS
    # ----------------------------------------------------
    ident_cols = ['date', 'year', 'state', 'region', 'lat', 'lng']
    feature_cols = [
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

    all_ordered_cols = ident_cols + feature_cols + target_cols
    final_df_valid = final_df_valid[all_ordered_cols]

    # Save to disk
    final_df_valid.to_csv(output_path, index=False)
    print(f"\nSuccessfully generated forecasting dataset -> {output_path}")
    print(f"Total valid prediction records: {len(final_df_valid)} (trimmed 30-day boundary rows)")

    # ----------------------------------------------------
    # AUTOMATED CHECKS & VERIFICATION
    # ----------------------------------------------------
    print("\n3. Running Automated Quality & Leakage Checks...")

    # Null checks
    null_counts = final_df_valid.isnull().sum()
    null_features = null_counts[null_counts > 0]
    if len(null_features) > 0:
        print("Feature Null Warnings:")
        print(null_features)
    else:
        print("[SUCCESS] Zero missing values across all feature and target columns.")

    # Target monotonicity verification
    mono_violations = 0
    for event in ['onset', 'break', 'heavy_rain']:
        v1 = (final_df_valid[f'{event}_7d'] > final_df_valid[f'{event}_14d']).sum()
        v2 = (final_df_valid[f'{event}_14d'] > final_df_valid[f'{event}_21d']).sum()
        v3 = (final_df_valid[f'{event}_21d'] > final_df_valid[f'{event}_30d']).sum()
        mono_violations += (v1 + v2 + v3)

    if mono_violations == 0:
        print("[SUCCESS] Target Monotonicity Verified: Target_7d <= Target_14d <= Target_21d <= Target_30d holds 100% of the time.")
    else:
        print(f"[WARNING] Monotonicity Violations Found: {mono_violations}")

    # Programmatic leakage check: correlation of future target vs past rainfall
    corr_past = final_df_valid['rainfall_7d_sum'].corr(final_df_valid['onset_7d'])
    print(f"Correlation between past 7d rainfall sum and future 7d onset target: {corr_past:.4f}")

    # Class balance table
    print("\n=== CLASS DISTRIBUTION SUMMARY across FORECAST HORIZONS ===")
    summary_rows = []
    for event, label in [('onset', 'Monsoon Onset'), ('break', 'Break Spell'), ('heavy_rain', 'Heavy Rain')]:
        row = {'Event': label}
        for N in [7, 14, 21, 30]:
            col = f'{event}_{N}d'
            pos_cnt = final_df_valid[col].sum()
            pct = final_df_valid[col].mean() * 100.0
            row[f'{N}D Target'] = f"{pos_cnt} ({pct:.2f}%)"
        summary_rows.append(row)

    dist_df = pd.DataFrame(summary_rows)
    print(dist_df.to_string(index=False))

    return final_df_valid

if __name__ == '__main__':
    build_forecasting_dataset()
