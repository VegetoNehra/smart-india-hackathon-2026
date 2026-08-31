import os
import pandas as pd
import numpy as np

def main():
    kaggle_csv = r'C:\Users\LENOVO\.cache\kagglehub\datasets\ankushnarwade\indian-climate-dataset-20242025\versions\1\Indian_Climate_Dataset_2024_2025.csv'
    forecast_csv = 'data/forecast_training_dataset.csv'
    output_dir = 'data/climate_experiments'
    os.makedirs(output_dir, exist_ok=True)

    output_dataset_path = os.path.join(output_dir, 'new_climate_forecast_dataset.csv')

    print("=== PHASE 5B BUILD NEW CLIMATE FORECASTING DATASET ===")
    print("1. Loading raw Kaggle daily climate dataset and forecasting dataset...")
    df_climate_raw = pd.read_csv(kaggle_csv)
    df_climate_raw['Date'] = pd.to_datetime(df_climate_raw['Date'])
    df_climate_raw['State'] = df_climate_raw['State'].str.strip()

    df_forecast = pd.read_csv(forecast_csv)
    df_forecast['date'] = pd.to_datetime(df_forecast['date'])

    print(f"Climate Daily Records: {len(df_climate_raw)} rows ({df_climate_raw['Date'].min().strftime('%Y-%m-%d')} to {df_climate_raw['Date'].max().strftime('%Y-%m-%d')})")
    print(f"Forecast Dataset Records: {len(df_forecast)} rows ({df_forecast['date'].min().strftime('%Y-%m-%d')} to {df_forecast['date'].max().strftime('%Y-%m-%d')})")

    # ---------------------------------------------------------
    # 2. FEATURE ENGINEERING ON DAILY CLIMATE DATA (STRICTLY <= T)
    # ---------------------------------------------------------
    print("2. Engineering multi-variable rolling climate features (strictly <= T)...")
    
    state_daily_list = []
    unique_states = df_climate_raw['State'].unique()

    for st in unique_states:
        st_df = df_climate_raw[df_climate_raw['State'] == st].sort_values('Date').copy()
        
        # Base daily features
        temp_avg = st_df['Temperature_Avg (℃)'].values if 'Temperature_Avg (℃)' in st_df.columns else st_df['Temperature_Avg (°C)'].values
        humidity = st_df['Humidity (%)'].values
        pressure = st_df['Pressure (hPa)'].values
        wind = st_df['Wind_Speed (km/h)'].values
        cloud = st_df['Cloud_Cover (%)'].values

        s_temp = pd.Series(temp_avg)
        s_hum = pd.Series(humidity)
        s_press = pd.Series(pressure)
        s_wind = pd.Series(wind)
        s_cloud = pd.Series(cloud)

        # Rolling means & changes (strictly <= date T)
        st_df['climate_temp_avg_today'] = temp_avg
        st_df['climate_temp_7d_mean'] = s_temp.rolling(7, min_periods=1).mean().values
        st_df['climate_temp_14d_mean'] = s_temp.rolling(14, min_periods=1).mean().values
        st_df['climate_temp_30d_mean'] = s_temp.rolling(30, min_periods=1).mean().values
        st_df['climate_temp_7d_change'] = (s_temp - s_temp.shift(7).bfill()).values

        st_df['climate_humidity_today'] = humidity
        st_df['climate_humidity_7d_mean'] = s_hum.rolling(7, min_periods=1).mean().values
        st_df['climate_humidity_14d_mean'] = s_hum.rolling(14, min_periods=1).mean().values
        st_df['climate_humidity_30d_mean'] = s_hum.rolling(30, min_periods=1).mean().values
        st_df['climate_humidity_7d_change'] = (s_hum - s_hum.shift(7).bfill()).values

        st_df['climate_pressure_today'] = pressure
        st_df['climate_pressure_7d_mean'] = s_press.rolling(7, min_periods=1).mean().values

        st_df['climate_wind_speed_today'] = wind
        st_df['climate_wind_7d_mean'] = s_wind.rolling(7, min_periods=1).mean().values

        st_df['climate_cloud_cover_today'] = cloud
        st_df['climate_cloud_cover_7d_mean'] = s_cloud.rolling(7, min_periods=1).mean().values

        state_daily_list.append(st_df)

    processed_climate_df = pd.concat(state_daily_list, ignore_index=True)

    # Compute National daily averages
    national_daily = processed_climate_df.groupby('Date')[[
        'climate_temp_avg_today', 'climate_temp_7d_mean', 'climate_temp_14d_mean', 'climate_temp_30d_mean', 'climate_temp_7d_change',
        'climate_humidity_today', 'climate_humidity_7d_mean', 'climate_humidity_14d_mean', 'climate_humidity_30d_mean', 'climate_humidity_7d_change',
        'climate_pressure_today', 'climate_pressure_7d_mean',
        'climate_wind_speed_today', 'climate_wind_7d_mean',
        'climate_cloud_cover_today', 'climate_cloud_cover_7d_mean'
    ]].mean().reset_index()
    national_daily['State'] = 'NATIONAL_AVG'

    climate_all = pd.concat([processed_climate_df, national_daily], ignore_index=True)

    # ---------------------------------------------------------
    # 3. VECTORIZED MERGE INTO FORECASTING DATASET
    # ---------------------------------------------------------
    print("3. Vectorized merging of daily weather features into forecasting dataset...")
    climate_feat_cols = [
        'climate_temp_avg_today', 'climate_temp_7d_mean', 'climate_temp_14d_mean', 'climate_temp_30d_mean', 'climate_temp_7d_change',
        'climate_humidity_today', 'climate_humidity_7d_mean', 'climate_humidity_14d_mean', 'climate_humidity_30d_mean', 'climate_humidity_7d_change',
        'climate_pressure_today', 'climate_pressure_7d_mean',
        'climate_wind_speed_today', 'climate_wind_7d_mean',
        'climate_cloud_cover_today', 'climate_cloud_cover_7d_mean'
    ]

    # Create month_day seasonal fallback lookup table
    climate_all['month_day'] = climate_all['Date'].dt.strftime('%m-%d')
    seasonal_state = climate_all.groupby(['State', 'month_day'])[climate_feat_cols].mean().reset_index()
    seasonal_national = climate_all[climate_all['State'] == 'NATIONAL_AVG'].groupby('month_day')[climate_feat_cols].mean().reset_index()

    # Create merge keys
    df_forecast['month_day'] = df_forecast['date'].dt.strftime('%m-%d')

    # Step A: Direct State + Date merge (for 2024-2025 where state exists)
    m1 = pd.merge(df_forecast, climate_all[['Date', 'State'] + climate_feat_cols], left_on=['date', 'state'], right_on=['Date', 'State'], how='left')

    # Step B: Direct National + Date merge (for 2024-2025 where state is not in climate dataset)
    m2 = pd.merge(m1, national_daily[['Date'] + climate_feat_cols], left_on='date', right_on='Date', suffixes=('', '_nat'), how='left')

    for col in climate_feat_cols:
        m2[col] = m2[col].fillna(m2[col + '_nat'])

    # Step C: Seasonal State fallback (for 2022-2023 train set)
    m3 = pd.merge(m2, seasonal_state, left_on=['state', 'month_day'], right_on=['State', 'month_day'], suffixes=('', '_sstate'), how='left')

    for col in climate_feat_cols:
        m3[col] = m3[col].fillna(m3[col + '_sstate'])

    # Step D: Seasonal National fallback
    m4 = pd.merge(m3, seasonal_national, left_on='month_day', right_on='month_day', suffixes=('', '_snat'), how='left')

    for col in climate_feat_cols:
        m4[col] = m4[col].fillna(m4[col + '_snat'])

    # Clean temporary merge columns
    drop_cols = [c for c in m4.columns if c.endswith('_nat') or c.endswith('_sstate') or c.endswith('_snat') or c in ['Date', 'State', 'month_day', 'Date_nat']]
    final_merged_df = m4.drop(columns=drop_cols)

    final_merged_df.to_csv(output_dataset_path, index=False)

    print(f"\nSuccessfully generated New Climate Forecasting Dataset -> {output_dataset_path}")
    print(f"Total Rows: {len(final_merged_df)} (preserved 100% of rows from forecast_training_dataset.csv)")
    print(f"Zero missing values in new climate features: {final_merged_df[climate_feat_cols].isnull().sum().sum() == 0}")

if __name__ == '__main__':
    main()
