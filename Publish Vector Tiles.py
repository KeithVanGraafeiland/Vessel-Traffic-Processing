import os

import arcpy
from credentials import username, password
from arcgis.gis import GIS
# Connect to GIS
gis = GIS("https://www.arcgis.com", username, password)
## Tested in ArcGIS Pro 2.8.3 (Released)

# Define Variables
vt_folder = r"D:\Temp\AIS\processing\Vector_Tiles"

vector_tile_package_list = []
for file in os.listdir(vt_folder):
    if file.endswith(".vtpk"):
        print(os.path.join(vt_folder, file))
        vector_tile_package_list.append(str(file))

def publish_vector_vector_tile_packages():
    for vector_tile_package in vector_tile_package_list:
        print("Publishing " + vector_tile_package)
        year = vector_tile_package.split("_")[3]
        month = vector_tile_package.split("_")[4]
        # group = vector_tile_package.split("_")[5]
        vt_package = vt_folder + "\\" + vector_tile_package
        # summary = "Monthly AIS Vessel Traffic Vector vector_tile_packages for " + year + " " + month + " " + group
        summary = "Monthly AIS Vessel Traffic Vector Tiles for " + year + " " + month
        tags = "AIS, Vessel Traffic, U.S. Vessel Traffic"
        credits = "NOAA, BOEM, USCG, Marine Cadastre, Esri"
        arcpy.management.SharePackage(vt_package, username, password, summary, tags, credits, "MYGROUPS", "Vessel Traffic","MYORGANIZATION", "TRUE", "AIS Vector Tiles")
        print("Published " + vector_tile_package)


publish_vector_vector_tile_packages()