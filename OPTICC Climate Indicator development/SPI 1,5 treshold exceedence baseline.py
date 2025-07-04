import os
import numpy as np
import rasterio
from rasterio.mask import mask
import geopandas as gpd
import pandas as pd

# === USER INPUTS ===
raster_folder = r"C:\510 project\SPI data"
adm2_shapefile = r"C:\510 project\Somalia Shapefile\9a01e8d3-9db9-4df7-85aa-38b5c3a4242c\som_admbnda_adm2_undp.shp"
output_risk_shapefile = r"C:\510 project\ADM2_Exceedance_Risk_Index_Baseline.shp"
spi_threshold = -1.5  # drought threshold

# === Load ADM2 shapefile ===
print("Loading admin boundaries...")
adm2 = gpd.read_file(adm2_shapefile).to_crs(epsg=4326)
adm2['geometry'] = adm2['geometry'].buffer(0)  # fix invalid geometries if any
adm2['adm2_id'] = adm2.index  # unique ID for merging

# === Load and sort SPI raster files ===
print("Loading raster files...")
spi_files = sorted([os.path.join(raster_folder, f) for f in os.listdir(raster_folder) if f.endswith('.tif')])

# === Initialize list to hold exceedance proportions per ADM2 per raster ===
results = []

print(f"Processing {len(spi_files)} raster files...")

for i, tif in enumerate(spi_files):
    print(f"Processing raster {i+1}/{len(spi_files)}: {os.path.basename(tif)}")
    with rasterio.open(tif) as src:
        for idx, row in adm2.iterrows():
            try:
                # Mask raster by ADM2 polygon
                out_image, out_transform = mask(src, [row['geometry']], crop=True)
                data = out_image[0]
                
                valid_mask = np.isfinite(data)
                total_valid_pixels = np.sum(valid_mask)
                
                if total_valid_pixels == 0:
                    exceedance_prop = np.nan
                else:
                    exceedance_mask = (data <= spi_threshold) & valid_mask
                    exceedance_prop = np.sum(exceedance_mask) / total_valid_pixels
                
                results.append({
                    'adm2_id': row['adm2_id'],
                    'time_index': i,
                    'exceedance_prop': exceedance_prop
                })
            except Exception as e:
                print(f"Error processing ADM2 {row['adm2_id']}: {e}")
                results.append({
                    'adm2_id': row['adm2_id'],
                    'time_index': i,
                    'exceedance_prop': np.nan
                })

# === Create DataFrame from results ===
df = pd.DataFrame(results)

# === Calculate mean exceedance proportion per ADM2 ===
print("Calculating mean exceedance proportion per ADM2...")
mean_exceedance = df.groupby('adm2_id')['exceedance_prop'].mean().reset_index()

# === Normalize mean exceedance proportion to 0-1 risk index ===
min_val = mean_exceedance['exceedance_prop'].min()
max_val = mean_exceedance['exceedance_prop'].max()

if max_val > min_val:
    mean_exceedance['risk_index'] = (mean_exceedance['exceedance_prop'] - min_val) / (max_val - min_val)
else:
    mean_exceedance['risk_index'] = mean_exceedance['exceedance_prop']  # all equal values

# === Merge risk index back to ADM2 GeoDataFrame ===
adm2 = adm2.merge(mean_exceedance[['adm2_id', 'risk_index']], on='adm2_id', how='left')

# === Save output shapefile ===
print("Saving output shapefile...")
adm2.to_file(output_risk_shapefile)

print("✅ Done! Risk index shapefile saved at:", output_risk_shapefile)



























