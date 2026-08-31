import pandas as pd
import numpy as np
import io
import os
import joblib
from xgboost import XGBRegressor

print("1. Loading Climate Indices...")
indices_df = pd.read_csv('data/climate_indices_merged.csv')
indices_df['Month'] = indices_df['Month'].str.upper()

# Map Month strings to Numbers
month_num_map = {
    'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6,
    'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12
}
indices_df['Month_Num'] = indices_df['Month'].map(month_num_map)

print("2. Loading Historical Rainfall (1901-2015)...")
rain_raw = pd.read_csv('data/rainfall in india 1901-2015.csv')
rain_raw.columns = rain_raw.columns.str.strip().str.upper()

# Melt columns (JAN, FEB...DEC) to rows
rain_melted = rain_raw.melt(
    id_vars=['SUBDIVISION', 'YEAR'], 
    value_vars=['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'],
    var_name='MONTH', 
    value_name='RAINFALL'
)
rain_melted['MONTH'] = rain_melted['MONTH'].str.upper()
rain_melted['MONTH_NUM'] = rain_melted['MONTH'].map(month_num_map)

# Map States to Subdivisions (Representative Mapping)
state_subdiv_map = {
    "Kerala": ["KERALA"],
    "Maharashtra": ["KONKAN & GOA", "MADHYA MAHARASHTRA", "MARATHWADA", "VIDARBHA"],
    "Assam": ["ASSAM & MEGHALAYA"],
    "Gujarat": ["GUJARAT REGION", "SAURASHTRA & KUTCH"],
    "Karnataka": ["COASTAL KARNATAKA", "NORTH INTERIOR KARNATAKA", "SOUTH INTERIOR KARNATAKA"],
    "Punjab": ["PUNJAB"],
    "Rajasthan": ["EAST RAJASTHAN", "WEST RAJASTHAN"],
    "Uttar Pradesh": ["EAST UTTAR PRADESH", "WEST UTTAR PRADESH"],
    "West Bengal": ["GANGETIC WEST BENGAL", "SUB HIMALAYAN WEST BENGAL & SIKKIM"]
}

# Group subdivisions into States
state_rain_records = []
for state, subdivs in state_subdiv_map.items():
    state_df = rain_melted[rain_melted['SUBDIVISION'].isin(subdivs)].copy()
    grouped = state_df.groupby(['YEAR', 'MONTH', 'MONTH_NUM'])['RAINFALL'].mean().reset_index()
    grouped['State'] = state
    state_rain_records.append(grouped)

historical_state_rain = pd.concat(state_rain_records, ignore_index=True)
historical_state_rain = historical_state_rain.rename(columns={'YEAR': 'Year', 'MONTH': 'Month', 'MONTH_NUM': 'Month_Num', 'RAINFALL': 'Rainfall'})

# Merge historical data with climate indices (1974 - 2015)
train_historical = pd.merge(indices_df, historical_state_rain, on=['Year', 'Month', 'Month_Num'], how='inner')
print(f"Historical training records (1974-2015): {train_historical.shape}")

print("3. Parsing Recent IMD Gridded Rainfall (2022-2025)...")
# Grid extraction setup for coordinates matching our seeded database regions
district_coords = {
    "Kerala": [
        {"name": "Wayanad", "lat": 11.6854, "lng": 76.1320},
        {"name": "Idukki", "lat": 9.8500, "lng": 76.9492}
    ],
    "Maharashtra": [
        {"name": "Pune", "lat": 18.5204, "lng": 73.8567},
        {"name": "Nashik", "lat": 20.0059, "lng": 73.7900}
    ],
    "Assam": [
        {"name": "Guwahati", "lat": 26.1445, "lng": 91.7362}
    ]
}

def extract_gridded_monthly_rainfall(year, lat, lng):
    filepath = f"data/Rainfall_ind{year}_rfp25.grd"
    if not os.path.exists(filepath):
        return None
    
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
            daily_rain.append(float(val) if val >= 0 else 0.0)
            
    # Convert daily list to monthly sum
    # Create date range for the target year
    dates = pd.date_range(start=f"{year}-01-01", periods=num_days, freq='D')
    df_daily = pd.DataFrame({'Date': dates, 'Rainfall': daily_rain})
    df_monthly = df_daily.groupby(df_daily['Date'].dt.month)['Rainfall'].sum().reset_index()
    return df_monthly

recent_records = []
for year in [2022, 2023, 2024, 2025]:
    for state, districts in district_coords.items():
        state_monthly_totals = []
        for dist in districts:
            monthly_rain = extract_gridded_monthly_rainfall(year, dist['lat'], dist['lng'])
            if monthly_rain is not None:
                state_monthly_totals.append(monthly_rain)
                
        if state_monthly_totals:
            # Average the districts to represent the state rainfall anomaly
            merged_districts = pd.concat(state_monthly_totals)
            state_avg = merged_districts.groupby('Date')['Rainfall'].mean().reset_index()
            
            # Match with climate indices for this year/month
            for idx, row in state_avg.iterrows():
                month_num = int(row['Date'])
                indices_match = indices_df[(indices_df['Year'] == year) & (indices_df['Month_Num'] == month_num)]
                if not indices_match.empty:
                    match_row = indices_match.iloc[0].to_dict()
                    match_row['State'] = state
                    match_row['Rainfall'] = row['Rainfall']
                    recent_records.append(match_row)

train_recent = pd.DataFrame(recent_records)
print(f"Recent gridded training records (2022-2025): {train_recent.shape}")

# Combine historical and gridded records
final_training_data = pd.concat([train_historical, train_recent], ignore_index=True)
print(f"Total training dataset size: {final_training_data.shape}")

# 4. Train XGBoost Model per State
features = ['Nino 3.4 SST Anomaly', 'SOI', 'ONI', 'RONI', 'IOD_Index', 'RMM1', 'RMM2', 'amplitude', 'phase', 'Month_Num']

# Ensure output services directory exists
os.makedirs('app/services', exist_ok=True)

trained_states = []
for state in final_training_data['State'].unique():
    state_data = final_training_data[final_training_data['State'] == state].copy()
    
    # Drop rows with NaN features or target
    state_data = state_data.dropna(subset=features + ['Rainfall'])
    
    if len(state_data) < 20:
        continue  # Need sufficient samples to train
        
    X = state_data[features]
    y = state_data['Rainfall']
    
    # Train XGBoost Regressor
    model = XGBRegressor(
        n_estimators=100,
        learning_rate=0.08,
        max_depth=4,
        random_state=42
    )
    model.fit(X, y)
    
    # Save model
    model_filename = f"app/services/xgboost_{state.lower().replace(' ', '_')}.joblib"
    joblib.dump(model, model_filename)
    print(f"Trained & Saved XGBoost model for {state} -> {model_filename}")
    trained_states.append(state)

print("ML Training Complete! Active prediction models successfully built.")
