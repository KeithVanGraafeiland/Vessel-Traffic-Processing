import arcpy
arcpy.env.overwriteOutput = True
tracks_db = r"C:\Users\keit8223\Documents\ArcGIS\Projects\AIS\Monthly_Vessel_Tracks.gdb"
chart_folder = r"C:\Users\keit8223\Documents\ArcGIS\Projects\AIS\AIS Processing\Chart_Products"
charts_fc = r"C:\Users\keit8223\Documents\ArcGIS\Projects\AIS\Data_Download_for_App\Chart_Index.gdb\App_Chart_Index_ENC_and_IENC_1"

# get track names
arcpy.env.workspace = tracks_db
tracks_list = []
for fc in arcpy.ListFeatureClasses():
    tracks_list.append(fc)
print(tracks_list)

# get chart names

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
    arcpy.management.CreateFileGDB(chart_folder, chart)


def clip_tracks(track_fc, chart_poly):
    # check to see if GDB exists or not - if not create it
    out_feature_class = chart_folder + "\\" + chart_poly + ".gdb" + "\\" + track_fc
    in_feature_class = tracks_db + "\\" + track_fc
    print(track_fc)
    where_clause = "\"Name\" = " + "\'" + chart_poly + "\'"
    print(where_clause)
    arcpy.management.SelectLayerByAttribute(charts_fc, "NEW_SELECTION",where_clause )
    arcpy.analysis.Clip(in_feature_class, charts_fc, out_feature_class)

for track in tracks_list:
    for chart in charts_list:
        clip_tracks(track,chart)