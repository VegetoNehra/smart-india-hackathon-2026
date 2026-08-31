import os
import glob
import pandas as pd
import numpy as np

def main():
    kaggle_path = r'C:\Users\LENOVO\.cache\kagglehub\datasets\venky73\temperatures-of-india\versions\1\temperatures.csv'
    output_dir = 'data/temperature'
    os.makedirs(output_dir, exist_ok=True)

    cleaned_csv_path = os.path.join(output_dir, 'cleaned_monthly_temperatures_1901_2017.csv')
    temp_forecast_csv_path = os.path.join(output_dir, 'temperature_forecast_dataset.csv')

    print("=== PHASE 5 TEMPERATURE DATA PREPROCESSING & AUDIT ===")
    if not os.path.exists(kaggle_path):
        raise FileNotFoundError(f"Kaggle temperature dataset not found at {kaggle_path}")

    print("1. Loading raw Kaggle temperature dataset...")
    df_raw = pd.read_csv(kaggle_path)
    df_raw.columns = df_raw.columns.str.strip().str.upper()

    print(f"Dataset shape: {df_raw.shape} ({len(df_raw)} years)")
    print(f"Year Range: {df_raw['YEAR'].min()} to {df_raw['YEAR'].max()}")

    # ---------------------------------------------------------
    # 2. DATA CLEANING & MELTING TO LONG FORMAT
    # ---------------------------------------------------------
    month_cols = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
    month_map = {'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6,
                 'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12}

    df_melted = df_raw.melt(
        id_vars=['YEAR'],
        value_vars=month_cols,
        var_name='MONTH',
        value_name='TEMP_CELSIUS'
    )
    df_melted['MONTH_NUM'] = df_melted['MONTH'].map(month_map)
    df_melted = df_melted.sort_values(['YEAR', 'MONTH_NUM']).reset_index(drop=True)

    # Compute 1981-2010 historical monthly normals (standard 30-year climatological normal baseline)
    climatology_base = df_melted[(df_melted['YEAR'] >= 1981) & (df_melted['YEAR'] <= 2010)]
    normals = climatology_base.groupby('MONTH_NUM')['TEMP_CELSIUS'].mean().to_dict()

    df_melted['MONTHLY_NORMAL_CELSIUS'] = df_melted['MONTH_NUM'].map(normals)
    df_melted['TEMP_ANOMALY_CELSIUS'] = df_melted['TEMP_CELSIUS'] - df_melted['MONTHLY_NORMAL_CELSIUS']

    # Export cleaned long format dataset
    df_melted.to_csv(cleaned_csv_path, index=False)
    print(f"Exported Cleaned Long Temperature Dataset -> {cleaned_csv_path}")

    # Summary Statistics
    print("\n[TEMPERATURE SUMMARY STATISTICS (1901-2017)]")
    print(f"Mean Temp:   {df_melted['TEMP_CELSIUS'].mean():.2f}°C")
    print(f"Min Temp:    {df_melted['TEMP_CELSIUS'].min():.2f}°C (Jan {df_raw.loc[df_raw['JAN'].idxmin(), 'YEAR']})")
    print(f"Max Temp:    {df_melted['TEMP_CELSIUS'].max():.2f}°C (May {df_raw.loc[df_raw['MAY'].idxmax(), 'YEAR']})")
    print(f"Null Values: {df_melted['TEMP_CELSIUS'].isnull().sum()}")

    # ---------------------------------------------------------
    # 3. MERGE CLIMATOLOGICAL TEMPERATURE FEATURES INTO FORECASTING DATASET
    # ---------------------------------------------------------
    print("\n3. Merging Climatological Temperature Features into 2022-2025 Forecasting Dataset...")
    forecast_path = 'data/forecast_training_dataset.csv'
    if not os.path.exists(forecast_path):
        raise FileNotFoundError(f"Forecasting dataset not found at {forecast_path}")

    df_forecast = pd.read_csv(forecast_path)
    df_forecast['date'] = pd.to_datetime(df_forecast['date'])

    # Historical monthly normals lookup (1901-2010 mean)
    all_time_normals = df_melted.groupby('MONTH_NUM')['TEMP_CELSIUS'].mean().to_dict()

    # Calculate month-to-month seasonal temperature change
    temp_changes = {}
    for m in range(1, 13):
        prev_m = 12 if m == 1 else m - 1
        temp_changes[m] = all_time_normals[m] - all_time_normals[prev_m]

    df_forecast['month_num'] = df_forecast['date'].dt.month

    # Map features
    df_forecast['climatological_temp_celsius'] = df_forecast['month_num'].map(all_time_normals)
    df_forecast['climatological_temp_normal_celsius'] = df_forecast['month_num'].map(normals)
    df_forecast['seasonal_temp_change_celsius'] = df_forecast['month_num'].map(temp_changes)

    df_forecast = df_forecast.drop(columns=['month_num'])

    # Export merged dataset
    df_forecast.to_csv(temp_forecast_csv_path, index=False)
    print(f"Exported Temperature-Enhanced Forecasting Dataset -> {temp_forecast_csv_path}")
    print(f"Total Rows: {len(df_forecast)} (preserved 100% of rows from forecast_training_dataset.csv)")
    print(f"Zero missing values in new temperature features: {df_forecast[['climatological_temp_celsius', 'climatological_temp_normal_celsius', 'seasonal_temp_change_celsius']].isnull().sum().sum() == 0}")

if __name__ == '__main__':
    main()
