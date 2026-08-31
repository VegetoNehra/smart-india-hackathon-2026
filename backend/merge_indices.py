import pandas as pd
import io

print("1. Parsing ENSO dataset...")
enso_df = pd.read_csv('data/dataset_enso.csv', encoding='latin-1')
# Strip leading/trailing whitespaces from column headers
enso_df.columns = enso_df.columns.str.strip()
# Keep relevant columns
enso_cols = ['Year', 'Month', 'Nino 3.4 SST Anomaly', 'SOI', 'ONI', 'RONI']
enso_df = enso_df[enso_cols].copy()
enso_df['Year'] = pd.to_numeric(enso_df['Year'], errors='coerce')
enso_df = enso_df.dropna(subset=['Year'])
enso_df['Year'] = enso_df['Year'].astype(int)
enso_df['Month'] = enso_df['Month'].str.upper()

print("2. Parsing IOD dataset...")
with open('data/IOD-index.csv', 'r') as f:
    iod_lines = [line.strip().replace('"', '') for line in f if line.strip()]
iod_raw = pd.read_csv(io.StringIO('\n'.join(iod_lines)), skiprows=1, sep=r'\s+')
# Melt IOD to long format
iod_df = iod_raw.melt(id_vars=['Year'], var_name='Month', value_name='IOD_Index')
iod_df['Year'] = pd.to_numeric(iod_df['Year'], errors='coerce')
iod_df = iod_df.dropna(subset=['Year'])
iod_df['Year'] = iod_df['Year'].astype(int)
iod_df['Month'] = iod_df['Month'].str.upper()

print("3. Parsing MJO dataset...")
with open('data/rmm.74toRealtime.csv', 'r') as f:
    mjo_lines = [line.strip().replace('"', '') for line in f if line.strip()]
mjo_data = []
for line in mjo_lines[2:]:
    parts = line.split()
    if len(parts) >= 7:
        mjo_data.append(parts[:7])
mjo_raw = pd.DataFrame(mjo_data, columns=['year', 'month', 'day', 'RMM1', 'RMM2', 'phase', 'amplitude'])
for col in mjo_raw.columns:
    mjo_raw[col] = pd.to_numeric(mjo_raw[col], errors='coerce')

# Map MJO month numbers to names (1 -> 'JAN')
month_map = {
    1: 'JAN', 2: 'FEB', 3: 'MAR', 4: 'APR', 5: 'MAY', 6: 'JUN',
    7: 'JUL', 8: 'AUG', 9: 'SEP', 10: 'OCT', 11: 'NOV', 12: 'DEC'
}
mjo_raw['Month'] = mjo_raw['month'].map(month_map)
mjo_raw = mjo_raw.rename(columns={'year': 'Year'})

# Aggregate MJO to monthly averages
mjo_monthly = mjo_raw.groupby(['Year', 'Month']).agg({
    'RMM1': 'mean',
    'RMM2': 'mean',
    'amplitude': 'mean',
    'phase': lambda x: x.value_counts().index[0] if not x.empty and x.value_counts().any() else None
}).reset_index()

print("4. Merging climate index datasets...")
# Merge ENSO and IOD
merged = pd.merge(enso_df, iod_df, on=['Year', 'Month'], how='inner')
# Merge with MJO
final_df = pd.merge(merged, mjo_monthly, on=['Year', 'Month'], how='inner')

print(f"Merge Complete! Final Dataset Shape: {final_df.shape}")
print(final_df.head(5))
final_df.to_csv('data/climate_indices_merged.csv', index=False)
