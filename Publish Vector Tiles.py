import os

import arcpy
from credentials import username, password
## Tested in ArcGIS Pro 2.8.3 (Released)

# Define Variables
vt_folder = r"E:\ArcGIS\Projects\AIS\processing\Vector_Tiles\Test"

tile_list = []
for file in os.listdir(vt_folder):
    if file.endswith(".vtpk"):
        print(os.path.join(vt_folder, file))
        tile_list.append(str(file))

# arcpy.env.workspace = vt_folder
# tile_list = os.listdir(vt_folder)
# print(tile_list)

def publish_vector_tiles():
    for tile in tile_list:
        print("Publishing " + tile)
        year = tile.split("_")[3]
        month = tile.split("_")[4]
        group = tile.split("_")[5]
        vt_package = vt_folder + "\\" + tile
        summary = "Monthly AIS Vessel Traffic Vector Tiles for " + year + " " + month + " " + group
        tags = "AIS, Vessel Traffic, Shipping"
        credits = "NOAA, BOEM, USCG, Marine Cadastre, Esri"
        arcpy.management.SharePackage(vt_package, username, password, summary, tags, credits, "MYGROUPS", "Vessel Traffic","MYORGANIZATION", "TRUE", "AIS Vector Tiles")


publish_vector_tiles()