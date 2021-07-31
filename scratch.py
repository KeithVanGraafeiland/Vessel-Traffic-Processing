import arcpy
from datetime import datetime
import os
import zipfile
from credentials import username, password

arcpy.env.overwriteOutput = True

# Define Variables

# Define Constants
TRACKS_DB = r"C:\Users\keit8223\Documents\ArcGIS\Projects\AIS\AIS Processing\Monthly_Vessel_Tracks.gdb"
CHART_FOLDER = r"C:\Users\keit8223\Documents\ArcGIS\Projects\AIS\AIS Processing\Chart_Products"
CHARTS_FC = r"C:\Users\keit8223\Documents\ArcGIS\Projects\AIS\AIS Processing\Chart_Index.gdb\App_Chart_Index_ENC_and_IENC"
APRX = arcpy.mp.ArcGISProject(r"C:\Users\keit8223\Documents\ArcGIS\Projects\AIS\AIS.aprx")
SYMBOLOGY_LAYER = r"C:\Users\keit8223\Documents\ArcGIS\Projects\AIS\AIS Processing\Vessel Traffic Layer Template Monthly.lyrx"
VT_FOLDER = r"C:\Users\keit8223\Documents\ArcGIS\Projects\AIS\AIS Processing\Vector_Tiles"
VT_INDEX = r"C:\Users\keit8223\Documents\ArcGIS\Projects\AIS\AIS Processing\Vector_Tile_Index.gdb\AIS_Vector_Tile_Index"


def log(message):
    print(message, datetime.now())


log("********** CREATE AIS CHART PRODUCTS **********")
start_time = datetime.now()

# get track names
log("Getting track names.....")
arcpy.env.workspace = TRACKS_DB
tracks_list = []
for fc in arcpy.ListFeatureClasses():
    tracks_list.append(fc)
print(tracks_list)

# get chart names
log("Getting chart names.....")
charts_list = []
chart_set = set()
rows = arcpy.SearchCursor(CHARTS_FC)
charts_field = "Name"
for row in rows:
    chart = row.getValue(charts_field)
    if chart not in chart_set:
        charts_list.append(chart)
        chart_set.add(chart)
    charts_list.sort()
print(charts_list)

for chart in charts_list:
    log("Creating GDB for " + chart + ".....")
    arcpy.management.CreateFileGDB(CHART_FOLDER, chart)


def clip_tracks(track_fc, chart_poly):
    # check to see if GDB exists or not - if not create it
    out_feature_class = CHART_FOLDER + "\\" + chart_poly + ".gdb" + "\\" + track_fc
    in_feature_class = TRACKS_DB + "\\" + track_fc
    where_clause = "\"Name\" = " + "\'" + chart_poly + "\'"
    chart_poly_lyr = chart_poly + "_lyr"
    log("Making feature layer for " + chart_poly + ".....")
    arcpy.management.MakeFeatureLayer(CHARTS_FC, chart_poly_lyr, where_clause)
    log("Clipping " + track_fc + " layer for " + chart_poly + ".....")
    arcpy.analysis.Clip(in_feature_class, chart_poly_lyr, out_feature_class)
    log("Done clipping " + track_fc + " layer for " + chart_poly + ".....")


def zip_charts():
    for chart in charts_list:
        gdb_file = CHART_FOLDER + "\\" + chart + ".gdb"
        gdb_name = os.path.basename(gdb_file)
        out_file = gdb_file[0:-4] + '.zip'
        with zipfile.ZipFile(out_file, mode='w',
                             compression=zipfile.ZIP_DEFLATED,
                             allowZip64=True) as myzip:
            for f in os.listdir(gdb_file):
                if f[-5:] != '.lock':
                    myzip.write(os.path.join(gdb_file, f), gdb_name + '\\' + os.path.basename(f))


def create_vector_tiles():
    vt_map = APRX.listMaps("Vector Tile*")[0]
    print(vt_map.name)
    for track in tracks_list:
        track_name = TRACKS_DB + "\\" + track
        vt_map.addDataFromPath(track_name)
        fc_layer = vt_map.listLayers("Vessel_Tracks*")[0]
        vt_package = VT_FOLDER + "\\" + track + ".vtpk"
        summary = "Monthly AIS Vessel Traffic Vector Tiles for " + track
        tags = "AIS, Vessel Traffic, Shipping"
        credits = "NOAA, BOEM, USGS, Marine Cadastre, Esri"
        print(fc_layer)
        arcpy.management.ApplySymbologyFromLayer(fc_layer, SYMBOLOGY_LAYER, "VALUE_FIELD vessel_group vessel_group",
                                                 "MAINTAIN")
        APRX.save()
        arcpy.management.CreateVectorTilePackage(vt_map, vt_package, "ONLINE", "", "INDEXED", 295828763.795777,
                                                 564.248588, VT_INDEX, summary, tags)
        arcpy.management.SharePackage(vt_package, username, password, summary, tags, credits, "MYGROUPS",
                                      "Vessel Traffic", "MYORGINIZATION", "TRUE", "AIS Vector Tiles")
        vt_map.remove_layer(fc_layer)
        APRX.save()


for track in tracks_list:
    for chart in charts_list:
        clip_tracks(track, chart)
zip_charts()
create_vector_tiles()
time_elapsed = datetime.now() - start_time
print('Time elapsed (hh:mm:ss.ms) {}'.format(time_elapsed))
log("********** CREATE AIS CHART PRODUCTS **********")
