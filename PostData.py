from arcgis.gis import GIS
from arcgis.features import FeatureLayer
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

# 1. Connect to your ArcGIS Online account (change if needed)
gis = GIS(
    os.getenv('ARCGIS_URL'),
    os.getenv('ARCGIS_USERNAME'),
    os.getenv('ARCGIS_PASSWORD')
    )

# 2. Load your data (e.g., from CSV)
df = pd.read_csv("your_data.csv") # Contains admin2pcode and ranking 

# 3. Load the existing admin boundary FeatureLayer
layer_url = "https://services.arcgis.com/.../FeatureServer/0"  # Replace with your actual Feature Layer URL
fl = FeatureLayer(layer_url)

# 4. Query all existing features
features = fl.query(where="1=1", out_fields="*", return_geometry=False).features

# 5. Match and update fields
updates = []
for feature in features:
    admin_code = feature.attributes.get("Admin02Cod")
    row = df[df["Admin02Cod"] == admin_code]
    if not row.empty:
        row_data = row.iloc[0]
        print(row_data)
        feature.attributes["Rank"] = row_data["Rank"]
        feature.attributes ["Alternative"] = row_data["Alternative"]
        feature.attributes ["Netflow"] = row_data ["Netflow"]
        feature.attributes ["PriorityAreas"] = row_data["PriorityAreas"]
        # Add other fields to update as needed
        updates.append(feature)

# 6. Send updates to the layer
if updates:
    response = fl.edit_features(updates=updates)
    print("Update response:", response)
else:
    print("No matches found to update.")
