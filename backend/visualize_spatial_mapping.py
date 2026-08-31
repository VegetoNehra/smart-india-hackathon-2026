import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def generate_spatial_visualizations():
    mapping_csv = 'data/spatial/admin_grid_mapping.csv'
    reports_dir = 'reports/phase4a'
    os.makedirs(reports_dir, exist_ok=True)

    if not os.path.exists(mapping_csv):
        print(f"Mapping dataset {mapping_csv} not found.")
        return

    df = pd.read_csv(mapping_csv)

    print("1. Generating Meerut District Grid Overlay Map...")
    # Filter Meerut Block and Panchayat records
    meerut_blocks = df[df['admin_level'] == 'Block']
    meerut_gps = df[df['admin_level'] == 'Gram Panchayat']

    fig, ax = plt.subplots(figsize=(10, 8))

    # Get IMD grid cells covering Meerut region (Lat 28.5 to 29.5, Lng 77.25 to 78.25)
    grid_cells = df[(df['grid_lat'] >= 28.5) & (df['grid_lat'] <= 29.5) & 
                    (df['grid_lng'] >= 77.25) & (df['grid_lng'] <= 78.25)][['grid_id', 'grid_lat', 'grid_lng']].drop_duplicates()

    # Draw IMD 0.25° grid cell boxes (centered at grid_lat, grid_lng -> box is [lat-0.125, lat+0.125])
    for _, g in grid_cells.iterrows():
        g_lat, g_lng = g['grid_lat'], g['grid_lng']
        rect = patches.Rectangle((g_lng - 0.125, g_lat - 0.125), 0.25, 0.25,
                                 linewidth=1, edgecolor='navy', facecolor='azure', alpha=0.4, linestyle='--')
        ax.add_patch(rect)
        ax.scatter(g_lng, g_lat, color='navy', marker='+', s=40, zorder=3)
        ax.text(g_lng, g_lat + 0.02, g['grid_id'], fontsize=7, color='darkblue', ha='center', fontweight='bold')

    # Plot Meerut 12 Block Centroids
    block_unique = meerut_blocks[['block', 'latitude', 'longitude']].drop_duplicates()
    ax.scatter(block_unique['longitude'], block_unique['latitude'], color='crimson', s=120, zorder=5, label='Meerut Block Centroid (12 Blocks)', marker='s')

    for _, b in block_unique.iterrows():
        ax.annotate(b['block'], (b['longitude'], b['latitude']), textcoords="offset points", xytext=(0, 6), ha='center', fontsize=9, fontweight='bold', color='maroon',
                    bbox=dict(boxstyle='round,pad=0.2', facecolor='yellow', alpha=0.7))

    # Plot Meerut Gram Panchayats
    gp_unique = meerut_gps[['panchayat', 'latitude', 'longitude']].drop_duplicates()
    ax.scatter(gp_unique['longitude'], gp_unique['latitude'], color='forestgreen', s=70, zorder=6, label='Gram Panchayat Centroid (Sample)', marker='^')

    for _, p in gp_unique.iterrows():
        ax.annotate(p['panchayat'], (p['longitude'], p['latitude']), textcoords="offset points", xytext=(0, -10), ha='center', fontsize=7, color='darkgreen')

    ax.set_title("Meerut District Spatial Hierarchy vs IMD 0.25° Grid Overlay", fontsize=13, fontweight='bold')
    ax.set_xlabel("Longitude (°E)", fontsize=11)
    ax.set_ylabel("Latitude (°N)", fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper left', fontsize=9)

    out_map1 = os.path.join(reports_dir, 'meerut_grid_overlay.png')
    plt.tight_layout()
    plt.savefig(out_map1, dpi=150)
    plt.close()
    print(f"Exported Meerut Overlay Map -> {out_map1}")

    # 2. National District Coverage Map
    print("2. Generating National District Spatial Coverage Chart...")
    fig, ax = plt.subplots(figsize=(10, 6))

    dist_df = df[df['admin_level'] == 'District'].drop_duplicates(subset=['state', 'district'])
    state_counts = dist_df['state'].value_counts().head(15)

    ax.barh(state_counts.index[::-1], state_counts.values[::-1], color='teal')
    ax.set_title("District Count Mapped to IMD 0.25° Grid (Top 15 States/UTs)", fontsize=12, fontweight='bold')
    ax.set_xlabel("Mapped District Count", fontsize=11)
    ax.grid(True, alpha=0.3)

    out_map2 = os.path.join(reports_dir, 'india_district_coverage.png')
    plt.tight_layout()
    plt.savefig(out_map2, dpi=150)
    plt.close()
    print(f"Exported District Coverage Map -> {out_map2}")

if __name__ == '__main__':
    generate_spatial_visualizations()
