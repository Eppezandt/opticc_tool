from arcgis.gis import GIS
from arcgis.features import FeatureLayer
import pandas as pd
import yaml
import os
from dotenv import load_dotenv

load_dotenv()

# Connect to your ArcGIS Online account (change if needed)
gis = GIS(
    os.getenv('ARCGIS_URL'),
    os.getenv('ARCGIS_USERNAME'),
    os.getenv('ARCGIS_PASSWORD')
    )

# Access the web map item
# List of Web Map item IDs
config = yaml.load("config/config.yaml")
webmap_ids= config["webmap_ids"]

# List to hold all tables
tables = []

# Loop through each Web Map
for wm_id in webmap_ids:
    try:
        print(f"\nProcessing Web Map: {wm_id}")
        webmap_item = gis.content.get(wm_id)
        webmap_data = webmap_item.get_data()
        operational_layers = webmap_data['operationalLayers']

        # Loop through layers in current web map
        for layer in operational_layers:
            try:
                print(f"  Fetching layer: {layer['title']}")
                fl = FeatureLayer(layer['url'])
                df = fl.query(where="1=1").sdf
                df['source_layer'] = layer['title']
                df['source_map'] = wm_id  # Track which map this came from
                tables.append(df)
            except Exception as e:
                print(f"  Failed to process layer '{layer['title']}': {e}")

    except Exception as e:
        print(f"Could not load WebMap {wm_id}: {e}")

# Merge and save
if tables:
    merged_df = pd.concat(tables, ignore_index=True)
    print("\nMerged table shape:", merged_df.shape)
    merged_df.to_csv("merged_webmap_table.csv", index=False)
    print("Saved to merged_webmap_table.csv")
else:
    print("No tables were found to merge.")
