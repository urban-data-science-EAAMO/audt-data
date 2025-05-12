#!/bin/bash
# [augmented urban data triangulation (audt)]
# [audt-data]
# [Pull]
# [Shell script for pull]
# [Matt Franchi]

# Get repository root
REPO_ROOT="$(git rev-parse --show-toplevel)"
SAVE_DIR="${REPO_ROOT}/audt_data/d01_data/geo/nyc"

# Create save directory
mkdir -p "${SAVE_DIR}"

# Geographic Boundaries 

## 2020 NYC Census Tracts, water areas clipped
wget -O "${SAVE_DIR}/ct-nyc-2020.geojson" 'https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/NYC_Census_Tracts_for_2020_US_Census/FeatureServer/0/query?where=1=1&outFields=*&outSR=4326&f=pgeojson'

## 2020 NYC Census Tracts, including water areas
wget -O "${SAVE_DIR}/ct-nyc-wi-2020.geojson" 'https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/NYC_Census_Tracts_for_2020_US_Census_Water_Included/FeatureServer/0/query?where=1=1&outFields=*&outSR=4326&f=pgeojson'

## 2020 NYC Census Blocks, including water areas 
wget -O "${SAVE_DIR}/cb-nyc-wi-2020.geojson" 'https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/NYC_Census_Blocks_for_2020_US_Census_Water_Included/FeatureServer/0/query?where=1=1&outFields=*&outSR=4326&f=pgeojson'

## 2020 NYC Census Blocks, water areas clipped
wget -O "${SAVE_DIR}/cb-nyc-2020.geojson" 'https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/NYC_Census_Blocks_for_2020_US_Census/FeatureServer/0/query?where=1=1&outFields=*&outSR=4326&f=pgeojson'

## NYC Integer 1 foot Digital Elevation Model Raster 
wget -O "${SAVE_DIR}/nyc-1ft-dem.zip" 'https://sa-static-customer-assets-us-east-1-fedramp-prod.s3.amazonaws.com/data.cityofnewyork.us/NYC_DEM_1ft_Int.zip'
unzip -d "${SAVE_DIR}" "${SAVE_DIR}/nyc-1ft-dem.zip"

# delete zip
rm "${SAVE_DIR}/nyc-1ft-dem.zip"