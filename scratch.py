import arcpy
from datetime import datetime
import os
import zipfile
arcpy.env.overwriteOutput = True

# Define Variables
tracks_db = r"C:\Users\keit8223\Documents\ArcGIS\Projects\AIS\AIS Processing\Monthly_Vessel_Tracks.gdb"
chart_folder = r"C:\Users\keit8223\Documents\ArcGIS\Projects\AIS\AIS Processing\Chart_Products"
charts_fc = r"C:\Users\keit8223\Documents\ArcGIS\Projects\AIS\AIS Processing\Chart_Index.gdb\App_Chart_Index_ENC_and_IENC_ODU"

def log(message):
    print(message,datetime.now())

log("********** CREATE AIS CHART PRODUCTS **********")
start_time = datetime.now()

# get track names
log("Getting track names.....")
arcpy.env.workspace = tracks_db
tracks_list = []
for fc in arcpy.ListFeatureClasses():
    tracks_list.append(fc)
print(tracks_list)

# get chart names
log("Getting chart names.....")
charts_list = []
chart_set = set()
rows = arcpy.SearchCursor(charts_fc)
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
    arcpy.management.CreateFileGDB(chart_folder, chart)


def clip_tracks(track_fc, chart_poly):
    # check to see if GDB exists or not - if not create it
    out_feature_class = chart_folder + "\\" + chart_poly + ".gdb" + "\\" + track_fc
    in_feature_class = tracks_db + "\\" + track_fc
    where_clause = "\"Name\" = " + "\'" + chart_poly + "\'"
    chart_poly_lyr = chart_poly + "_lyr"
    log("Making feature layer for " + chart_poly + ".....")
    arcpy.management.MakeFeatureLayer(charts_fc, chart_poly_lyr, where_clause)
    log("Clipping " + track_fc + " layer for " + chart_poly + ".....")
    arcpy.analysis.Clip(in_feature_class, chart_poly_lyr, out_feature_class)
    log("Done clipping " + track_fc + " layer for " + chart_poly + ".....")

def zip_charts():
    for chart in charts_list:
        gdbFile = chart_folder + "\\" + chart + ".gdb"
        gdbName = os.path.basename(gdbFile)
        outFile = gdbFile[0:-4] + '.zip'
        with zipfile.ZipFile(outFile, mode='w',
                             compression=zipfile.ZIP_DEFLATED,
                             allowZip64=True) as myzip:
            for f in os.listdir(gdbFile):
                if f[-5:] != '.lock':
                    myzip.write(os.path.join(gdbFile, f), gdbName + '\\' + os.path.basename(f))

for track in tracks_list:
    for chart in charts_list:
        clip_tracks(track,chart)
zip_charts()
time_elapsed = datetime.now() - start_time
print('Time elapsed (hh:mm:ss.ms) {}'.format(time_elapsed))
log("********** CREATE AIS CHART PRODUCTS **********")