import os
import arcpy
from credentials import username, password
arcpy.env.overwriteOutput = True
## Tested in ArcGIS Pro 2.8.3 (Released)

# Define Variables
aprx = arcpy.mp.ArcGISProject(r'F:\ArcGIS\Projects\AIS\AIS.aprx')
symbology_layer = r"F:\ArcGIS\Projects\AIS\processing\Vessel Traffic Layer Template Monthly.lyrx"
symbology_gen_layer = r"F:\ArcGIS\Projects\AIS\processing\Vessel Traffic Layer Template Monthly gen.lyrx"
vt_folder = r"F:\ArcGIS\Projects\AIS\processing\Vector_Tiles"
vt_index_gdb = os.path.join(vt_folder,"vector_tile.gdb")
# vt_index = os.path.join(vt_index_gdb,"vector_tile_index")
tracks_db = r"F:\ArcGIS\Projects\AIS\processing\Monthly_Vessel_Tracks.gdb"

arcpy.env.workspace = tracks_db



if arcpy.Exists(vt_index_gdb):
    pass
else:
    arcpy.management.CreateFileGDB(vt_folder,"vector_tile.gdb")
    

def create_vector_tiles():
    tracks_list = []
    for fc in arcpy.ListFeatureClasses('US_Vessel_Traffic_2018*'):
        tracks_list.append(fc)
    print(tracks_list)
    
    for track in tracks_list:
        if "gen" in track:
            pass
        else:
            vt_map = aprx.listMaps("Vector Tile*")[0]
            print(vt_map.name)           
            track_name = tracks_db + "\\" + track
            trackgen_name = tracks_db + "\\" + track + "_gen"
            index_name = vt_index_gdb + "\\" + track + "index"
            # vt_map.addDataFromPath(trackgen_name)
            # vt_map.addDataFromPath(track_name)
            vt_package = vt_folder + "\\" + track + "_scaled.vtpk"
            global fc_layer
            global fc_gen_layer
            fc_layer = vt_map.listLayers()[0]
            fc_gen_layer = vt_map.listLayers()[1]
            print(fc_layer, fc_gen_layer)
            current_data_source = fc_layer.connectionProperties
            current_gen_data_source = fc_gen_layer.connectionProperties
            new_data_source = {
                        'connection_info': {'database': tracks_db},  # Update as necessary
                        'dataset': track,  # Update as necessary
                        'workspace_factory': 'File Geodatabase'  # Or other type as necessary
                    }
            new_gen_data_source = {
            'connection_info': {'database': tracks_db},  # Update as necessary
            'dataset': track + "_gen",  # Update as necessary
            'workspace_factory': 'File Geodatabase'  # Or other type as necessary
                    }   
            fc_layer.updateConnectionProperties(current_data_source, new_data_source)
            fc_gen_layer.updateConnectionProperties(current_gen_data_source, new_gen_data_source)
            fc_layer.maxThreshold=0
            fc_layer.minThreshold=50000
            fc_gen_layer.maxThreshold=50000
            fc_gen_layer.minThreshold=0
            summary = "Monthly AIS Vessel Traffic Vector Tiles for " + track
            tags = "AIS, Vessel Traffic, U.S. Vessel Traffic"
            credits = "NOAA, BOEM, USCG, Marine Cadastre, Esri"
            # arcpy.management.ApplySymbologyFromLayer(fc_layer,symbology_layer,"VALUE_FIELD vessel_group vessel_group", "MAINTAIN")
            # arcpy.management.ApplySymbologyFromLayer(fc_gen_layer,symbology_gen_layer,"VALUE_FIELD vessel_group vessel_group", "MAINTAIN")
            print(track_name)
            print(index_name)
            print(fc_layer)
            print(vt_package)
            aprx.save()
            
            arcpy.management.CreateVectorTileIndex(
                in_map=vt_map,
                out_featureclass=index_name,
                service_type="ONLINE",
                tiling_scheme=None,
                vertex_count=10000
            )
            aprx.save()

            arcpy.management.CreateVectorTilePackage(vt_map, vt_package, "ONLINE", "", "INDEXED", 295828763.795777, 564.248588, index_name, summary, tags)
            arcpy.management.SharePackage(vt_package, username, password, summary, tags, credits, "MYGROUPS", "Vessel Traffic","MYORGANIZATION", "TRUE", "AIS Vector Tiles")
            # vt_map.removeLayer(fc_layer)
            # vt_map.removeLayer(fc_gen_layer)
            aprx.save()

create_vector_tiles()