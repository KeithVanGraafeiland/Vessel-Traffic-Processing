import arcpy
from credentials import username, password

# Define Variables
aprx = arcpy.mp.ArcGISProject(r"C:\Users\keit8223\Documents\ArcGIS\Projects\AIS\AIS.aprx")
symbology_layer = r"C:\Users\keit8223\Documents\ArcGIS\Projects\AIS\AIS Processing\Vessel Traffic Layer Template Monthly.lyrx"
vt_folder = r"C:\Users\keit8223\Documents\ArcGIS\Projects\AIS\AIS Processing\Vector_Tiles"
vt_index = r"C:\Users\keit8223\Documents\ArcGIS\Projects\AIS\AIS Processing\Vector_Tile_Index.gdb\AIS_Vector_Tile_Index"
tracks_db = r"C:\Users\keit8223\Documents\ArcGIS\Projects\AIS\AIS Processing\TEST_DATA_ONLY\Monthly_Vessel_Tracks.gdb"


arcpy.env.workspace = tracks_db
tracks_list = []
for fc in arcpy.ListFeatureClasses():
    tracks_list.append(fc)
print(tracks_list)

def create_vector_tiles():
    vt_map = aprx.listMaps("Vector Tile*")[0]
    print(vt_map.name)
    for track in tracks_list:
        track_name = tracks_db + "\\" + track
        vt_map.addDataFromPath(track_name)
        fc_layer = vt_map.listLayers("Vessel_Tracks*")[0]
        vt_package = vt_folder + "\\" + track + ".vtpk"
        summary = "Monthly AIS Vessel Traffic Vector Tiles for " + track
        tags = "AIS, Vessel Traffic, Shipping"
        credits = "NOAA, BOEM, USGS, Marine Cadastre, Esri"
        print(fc_layer)
        arcpy.management.ApplySymbologyFromLayer(fc_layer,symbology_layer,"VALUE_FIELD vessel_group vessel_group", "MAINTAIN")
        aprx.save()
        arcpy.management.CreateVectorTilePackage(vt_map, vt_package, "ONLINE", "", "INDEXED", 295828763.795777, 564.248588, vt_index, summary, tags)
        arcpy.management.SharePackage(vt_package, username, password, summary, tags, credits, "MYGROUPS", "Vessel Traffic","MYORGINIZATION", "TRUE", "AIS Vector Tiles")
        vt_map.remove_layer(fc_layer)
        aprx.save()
