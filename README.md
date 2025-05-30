# opticc_tool

OPTICC is a priority zone selection tool. It aims to address this complexity by developing a structured methodology for geospatial prioritization. By systematically combining and analyzing these overlapping datasets, OPTICC will provide a robust framework to support the definition of priority zones, ensuring that decisions are data informed, transparent, and operationally relevant. This approach will enhance ability to anticipate risks, allocate resources effectively, and improve programmatic planning in dynamic and high-risk environments.

## AVAILABLE SCRIPTS 
### 1. `Data.py`

- This script is used to extract the attribute tables for the layers created in ArcGIS. 
- The script makes use of the ArcGIS library to do this extraction
- The script makes use of the web ids to connect to the webmaps which contain various feature layers
- The different layers have been put into the following webmaps;
    - OPTICC Development BB (Here you can get the climate indicators, and the world pop). 
    - CCVI (Here you get the layers for socio-economic vulnerability)
    - OPTICC Development (As Eppe has created this webmap, its likely he will add more feature layers here.
    - Important to check that the webmaps do not have duplicate feature layers
- The output file from this script is a merged web map table (CSV) which contains all the indicators values per admin area 2
### 2. `Electre II.py`
- The merged web map table is used as input in ELECTRE II. The ELECTRE II script expects an input of a CSV file (top row has the indicator names, second row has the weights, and the first column has the alternatives = adminpcodes)
- See example dataset called climateindicators
- When the ELECTRE II script is run, you get an output of the final ranking of the areas. This will show up as (Alternative = Admpcode; the rank; netflow). This final ranking is what will be visualized in ArcGIS. 
- See example output called Electre_ranking
### 3. `Postdata.py`
- We use this script to push the outputs from ELECTRE II back to ArcGIS for the visualization
- We use the admin pcode as a link to the admin boundaries layer in ArcGIS. 
- The layer with your admin boundaries (admin level 2) that is in ArcGIS has a URL. This URL should be defined in the script
- What the script is doing here is a Join by attribute. It will look for the common key (so admin p code in your layer on ArcGIS and the admin pcode from your output from ELECTRE II). Based on these two fields, the join will occur. 
- For the layer in ArcGIS (make sure to create new fields that will be filled in by the data from the ELECTRE II output i.e. in ArcGIS, create fields Alternatives, Rank, Netflow
- Once you run the script, the data from the ELECTRE analysis will be added to the ArcGIS admin boundary layer (the values will be filled into the fields created)
- This appended layer will be used for the visualization 

## WORK IN PROGRESS
- We are currently not getting data directly from the source (we are manually downloading this data except for CCVI data because they have an API connection). We need a script or scripts to automatically get data. Some example scripts have been shared by British Red Cross
- We are currently doing the data processing manually in ArcGIS (so aggregating all the data to admin level 2), doing any clipping and any other processing. So we would need to have a script that can be easily applied to do this processing
- What we want from the processed data is an input for ELECTRE II which needs to be (The admin area + the indicator values/admin area)
- We need all these scripts to work together as part of a workflow. Currently these scripts are running independently and produce independent outputs that need to be adjusted and fed into the next script.
