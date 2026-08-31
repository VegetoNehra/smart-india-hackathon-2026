import os
import glob
import numpy as np
import pandas as pd

def load_grd_daily_data(filepath, row_idx, col_idx, num_cols=135, num_rows=129):
    """
    Parses binary 0.25 x 0.25 IMD gridded daily rainfall data (.grd) for specific grid cell.
    """
    if not os.path.exists(filepath):
        return None

    filename = os.path.basename(filepath)
    year = int(''.join(filter(str.isdigit, filename))[:4])

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
            daily_rain.append(float(val) if val >= 0 else 0.0)

    dates = pd.date_range(start=f"{year}-01-01", periods=num_days, freq='D')
    return pd.DataFrame({'date': dates, 'rainfall': daily_rain, 'year': year})

def main():
    spatial_dir = 'data/spatial'
    os.makedirs(spatial_dir, exist_ok=True)
    output_csv = os.path.join(spatial_dir, 'meerut_block_forecast_dataset.csv')

    print("1. Loading spatial grid mapping and climate/event datasets...")
    admin_map_df = pd.read_csv('data/spatial/admin_grid_mapping.csv')
    block_mappings = admin_map_df[admin_map_df['admin_level'] == 'Block'].copy()

    df_climate = pd.read_csv('data/climate_indices_merged.csv')
    df_climate['Month'] = df_climate['Month'].str.upper()
    month_to_num = {'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6,
                    'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12}
    df_climate['month_num'] = df_climate['Month'].map(month_to_num)

    df_station_daily = pd.read_csv('data/forecast_training_dataset.csv')
    df_station_daily['date'] = pd.to_datetime(df_station_daily['date'])
    up_station_daily = df_station_daily[df_station_daily['state'] == 'Uttar Pradesh'].sort_values('date').copy()

    grd_files = sorted(glob.glob('data/Rainfall_ind*.grd'))
    print(f"Found {len(grd_files)} daily gridded binary files (.grd).")

    # Get unique grid cells needed for Meerut blocks
    unique_grids = block_mappings[['grid_id', 'grid_lat', 'grid_lng']].drop_duplicates().reset_index(drop=True)
    grid_data_dict = {}

    print("2. Parsing daily rainfall for IMD grid cells covering Meerut Blocks...")
    for _, g_row in unique_grids.iterrows():
        g_id = g_row['grid_id']
        g_lat, g_lng = g_row['grid_lat'], g_row['grid_lng']
        row_idx = int((g_lat - 6.5) / 0.25)
        col_idx = int((g_lng - 66.5) / 0.25)

        series_list = []
        for filepath in grd_files:
            s_df = load_grd_daily_data(filepath, row_idx, col_idx)
            if s_df is not None:
                series_list.append(s_df)

        if series_list:
            grid_series = pd.concat(series_list, ignore_index=True)
            grid_series = grid_series.sort_values('date').reset_index(drop=True)
            grid_data_dict[g_id] = grid_series.set_index('date')['rainfall'].to_dict()

    print("3. Building Block-level spatial features for Meerut's 12 Blocks...")
    block_unique_names = block_mappings['block'].unique()
    processed_block_dfs = []

    for block_name in block_unique_names:
        b_map = block_mappings[block_mappings['block'] == block_name].sort_values('mapping_rank')
        b_lat = b_map['latitude'].iloc[0]
        b_lng = b_map['longitude'].iloc[0]
        near_dist_km = b_map['distance_km'].iloc[0]

        # Extract grid IDs and weights
        g_ids = b_map['grid_id'].values
        g_weights = b_map['proximity_weight'].values

        # Build daily series for this block using station dates as reference
        block_dates = up_station_daily['date'].values
        n_dates = len(block_dates)

        idw_rain = np.zeros(n_dates, dtype=float)
        grid_mean = np.zeros(n_dates, dtype=float)
        grid_std = np.zeros(n_dates, dtype=float)
        grid_min = np.zeros(n_dates, dtype=float)
        grid_max = np.zeros(n_dates, dtype=float)
        grid_range = np.zeros(n_dates, dtype=float)

        for d_idx, dt in enumerate(block_dates):
            # Parse rain from 4 surrounding grid cells for this date
            cell_vals = []
            for g_id in g_ids:
                val = grid_data_dict.get(g_id, {}).get(pd.to_datetime(dt), 0.0)
                cell_vals.append(val)

            cell_vals = np.array(cell_vals)
            idw_val = np.sum(g_weights * cell_vals)

            idw_rain[d_idx] = idw_val
            grid_mean[d_idx] = np.mean(cell_vals)
            grid_std[d_idx] = np.std(cell_vals)
            grid_min[d_idx] = np.min(cell_vals)
            grid_max[d_idx] = np.max(cell_vals)
            grid_range[d_idx] = np.max(cell_vals) - np.min(cell_vals)

        block_df = pd.DataFrame({
            'date': block_dates,
            'state': 'Uttar Pradesh',
            'district': 'Meerut',
            'block': block_name,
            'latitude': b_lat,
            'longitude': b_lng,
            'nearest_grid_distance': near_dist_km,
            'spatial_rainfall_today': idw_rain,
            'grid_rainfall_mean': grid_mean,
            'grid_rainfall_std': grid_std,
            'grid_rainfall_min': grid_min,
            'grid_rainfall_max': grid_max,
            'grid_rainfall_range': grid_range
        })

        # ----------------------------------------------------
        # SPATIAL ROLLING FEATURES (STRICTLY <= DATE T)
        # ----------------------------------------------------
        s_rain = block_df['spatial_rainfall_today'].values
        
        block_df['spatial_rainfall_3d_sum'] = pd.Series(s_rain).rolling(3, min_periods=1).sum().values
        block_df['spatial_rainfall_7d_sum'] = pd.Series(s_rain).rolling(7, min_periods=1).sum().values
        block_df['spatial_rainfall_14d_sum'] = pd.Series(s_rain).rolling(14, min_periods=1).sum().values
        block_df['spatial_rainfall_30d_sum'] = pd.Series(s_rain).rolling(30, min_periods=1).sum().values

        block_df['spatial_rainfall_7d_mean'] = pd.Series(s_rain).rolling(7, min_periods=1).mean().values
        block_df['spatial_rainfall_14d_mean'] = pd.Series(s_rain).rolling(14, min_periods=1).mean().values
        block_df['spatial_rainfall_30d_mean'] = pd.Series(s_rain).rolling(30, min_periods=1).mean().values

        block_df['spatial_rainfall_7d_max'] = pd.Series(s_rain).rolling(7, min_periods=1).max().values
        block_df['spatial_rainfall_14d_max'] = pd.Series(s_rain).rolling(14, min_periods=1).max().values
        block_df['spatial_rainfall_30d_max'] = pd.Series(s_rain).rolling(30, min_periods=1).max().values

        # Streaks
        consec_dry = np.zeros(n_dates, dtype=int)
        consec_rain = np.zeros(n_dates, dtype=int)
        c_dry, c_rain = 0, 0
        for i in range(n_dates):
            r_v = s_rain[i]
            if r_v < 1.0:
                c_dry += 1
                c_rain = 0
            else:
                c_dry = 0

            if r_v >= 2.5:
                c_rain += 1
            else:
                c_rain = 0

            consec_dry[i] = c_dry
            consec_rain[i] = c_rain

        block_df['spatial_consecutive_dry_days'] = consec_dry
        block_df['spatial_consecutive_rain_days'] = consec_rain

        # ----------------------------------------------------
        # MERGE STATION & CLIMATE FEATURES AND TARGETS
        # ----------------------------------------------------
        merged_block = pd.merge(
            block_df,
            up_station_daily.drop(columns=['state', 'region', 'lat', 'lng']),
            on='date',
            how='left'
        )

        processed_block_dfs.append(merged_block)

    final_spatial_df = pd.concat(processed_block_dfs, ignore_index=True)
    final_spatial_df = final_spatial_df.sort_values(['block', 'date']).reset_index(drop=True)

    # Save to disk
    final_spatial_df.to_csv(output_csv, index=False)
    print(f"\nSuccessfully generated Block-Level Spatial Dataset -> {output_csv}")
    print(f"Total Block-Daily Records: {len(final_spatial_df)} (12 Blocks x {n_dates} dates)")

    # Data Quality Verification
    null_counts = final_spatial_df.isnull().sum()
    null_cols = null_counts[null_counts > 0]
    if len(null_cols) == 0:
        print("[SUCCESS] Zero missing values across all spatial feature and target columns.")
    else:
        print("Feature Null Warnings:")
        print(null_cols)

if __name__ == '__main__':
    main()
