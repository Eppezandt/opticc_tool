import os
import numpy as np
import rasterio
from rasterio.merge import merge
from rasterio.features import shapes
import geopandas as gpd
from shapely.geometry import shape
import pandas as pd

# === USER INPUTS ===
raster_folder = r"C:\510 project\SPI data"
output_risk_shapefile = r"C:\510 project\SPI_drought_index_vector.shp"
output_spi_shapefile = r"C:\510 project\SPI_average_vector.shp"
buffer_km = 150  # Buffer around Somalia in kilometers
adm2_shapefile = r"C:\510 project\Somalia Shapefile\9a01e8d3-9db9-4df7-85aa-38b5c3a4242c\som_admbnda_adm2_undp.shp"

# === STEP 1: Load and buffer Somalia boundary ===
print("Buffering Somalia boundary...")
somalia = gpd.read_file(adm2_shapefile).to_crs(epsg=3857)
somalia_buffered = somalia.unary_union.buffer(buffer_km * 1000)  
somalia_buffered = gpd.GeoDataFrame(geometry=[somalia_buffered], crs=somalia.crs).to_crs(epsg=4326)

# === STEP 2: Load and merge SPI rasters ===
print("Merging SPI rasters...")
spi_files = sorted([os.path.join(raster_folder, f) for f in os.listdir(raster_folder) if f.endswith('.tif')])
srcs = [rasterio.open(f) for f in spi_files]
mosaic, out_trans = merge(srcs)
meta = srcs[0].meta.copy()
for src in srcs:
    src.close()

# === STEP 3: Calculate average SPI ===
print("Calculating average SPI...")
valid_mask = np.isfinite(mosaic)
valid_counts = valid_mask.sum(axis=0)
spi_sum = np.nansum(np.where(valid_mask, mosaic, 0), axis=0)
average_spi = np.divide(spi_sum, valid_counts, where=valid_counts != 0)

# === STEP 4: Define interpolated risk index function ===
def assign_risk_index_interpolated(spi_value):
    if spi_value <= -2.0:
        return 1.0
    elif -2.0 < spi_value <= -1.5:
        return 1.0 + (spi_value + 2.0) * (0.8 - 1.0) / (0.5)
    elif -1.5 < spi_value <= -1.0:
        return 0.8 + (spi_value + 1.5) * (0.6 - 0.8) / (0.5)
    elif -1.0 < spi_value <= 1.0:
        return 0.6 + (spi_value + 1.0) * (0.4 - 0.6) / (2.0)
    elif 1.0 < spi_value <= 1.5:
        return 0.4 + (spi_value - 1.0) * (0.2 - 0.4) / (0.5)
    elif 1.5 < spi_value <= 2.0:
        return 0.2 + (spi_value - 1.5) * (0.0 - 0.2) / (0.5)
    else:
        return 0.0

# === STEP 5: Calculate interpolated Risk Index ===
print("Calculating interpolated Risk Index...")
risk_index = np.vectorize(assign_risk_index_interpolated)(average_spi)

# === STEP 6: Convert average SPI raster to vector polygons ===
print("Converting average SPI raster to vector polygons...")
mask = ~np.isnan(average_spi)
shapes_gen_spi = shapes(average_spi.astype('float32'), mask=mask, transform=out_trans)

records_spi = []
for geom, val in shapes_gen_spi:
    records_spi.append({'geometry': shape(geom), 'average_spi': float(val)})

gdf_spi = gpd.GeoDataFrame(records_spi, crs='EPSG:4326')
gdf_spi_clipped = gdf_spi[gdf_spi.geometry.intersects(somalia_buffered.geometry[0])]

# === STEP 7: Convert risk index raster to vector polygons ===
print("Converting Risk Index raster to vector polygons...")
mask_risk = ~np.isnan(risk_index)
shapes_gen_risk = shapes(risk_index.astype('float32'), mask=mask_risk, transform=out_trans)

records_risk = []
for geom, val in shapes_gen_risk:
    records_risk.append({'geometry': shape(geom), 'risk_index': float(val)})

gdf_risk = gpd.GeoDataFrame(records_risk, crs='EPSG:4326')
gdf_risk_clipped = gdf_risk[gdf_risk.geometry.intersects(somalia_buffered.geometry[0])]

# === STEP 8: Reproject GeoDataFrames to EPSG:3857 ===
print("Reprojecting to EPSG:3857 (Web Mercator)...")
gdf_spi_clipped = gdf_spi_clipped.to_crs(epsg=3857)
gdf_risk_clipped = gdf_risk_clipped.to_crs(epsg=3857)

# === STEP 9: Save outputs ===
print("Saving shapefiles...")
gdf_spi_clipped.to_file(output_spi_shapefile)
gdf_risk_clipped.to_file(output_risk_shapefile)
























