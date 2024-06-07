import arcpy
from credentials import username, password
arcpy.env.overwriteOutput = True
## Tested in ArcGIS Pro 2.8.3 (Released)

# Define Variables
aprx = arcpy.mp.ArcGISProject(r"C:\Users\Administrator\Documents\ArcGIS\Projects\AIS\AIS.aprx")
symbology_layer = r"D:\AIS_Processing\Vessel Traffic Layer Template Monthly.lyrx"
vt_folder = r"D:\AIS_Processing\Vector_Tiles\R_03"
vt_index = r"D:\AIS_Processing\Vector_Tile_Index.gdb\AIS_Vector_Tile_Index"
tracks_db = r"D:\AIS_Processing\Monthly_Vessel_Tracks_by_Group.gdb"
vt_index_gdb = r"D:\AIS_Processing\Vector_Tile_Index.gdb"

arcpy.env.workspace = tracks_db
tracks_list = []
for fc in arcpy.ListFeatureClasses("*2016_01*"):
    tracks_list.append(fc)
print(tracks_list)

def create_vector_tiles():
    vt_map = aprx.listMaps("Vector Tile*")[0]
    print(vt_map.name)
    for track in tracks_list:
        track_name = tracks_db + "\\" + track
        index_name = vt_index_gdb + "\\" + track + "index"
        vt_map.addDataFromPath(track_name)
        fc_layer = vt_map.listLayers()[0]
        vt_package = vt_folder + "\\" + track + ".vtpk"
        summary = "Monthly AIS Vessel Traffic Vector Tiles for " + track
        tags = "AIS, Vessel Traffic, U.S. Vessel Traffic"
        credits = "NOAA, BOEM, USCG, Marine Cadastre, Esri"
        print(track_name)
        print(index_name)
        print(fc_layer)
        print(vt_package)
        # arcpy.management.ApplySymbologyFromLayer(fc_layer,symbology_layer,"VALUE_FIELD vessel_group vessel_group", "MAINTAIN")
        aprx.save()
        arcpy.management.CreateVectorTileIndex(
            in_map=vt_map,
            out_featureclass=index_name,
            service_type="ONLINE",
            tiling_scheme=None,
            vertex_count=10000
        )
        arcpy.management.CreateVectorTilePackage(vt_map, vt_package, "ONLINE", "", "INDEXED", 295828763.795777, 564.248588, vt_index, summary, tags)
        # arcpy.management.SharePackage(vt_package, username, password, summary, tags, credits, "MYGROUPS", "Vessel Traffic","MYORGANIZATION", "TRUE", "AIS Vector Tiles")
        vt_map.removeLayer(fc_layer)
        aprx.save()

create_vector_tiles()