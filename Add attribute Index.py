import arcpy

tracks_db = r"D:\AIS_Processing\Monthly_Tracks_by_Year\Vessel_Tracks_2020.gdb"

arcpy.env.workspace = tracks_db
tracks_list = []
for fc in arcpy.ListFeatureClasses():
    tracks_list.append(fc)
print(tracks_list)

def add_attribute_index():
    for track in tracks_list:
        fields1 = ["start_date", "end_date"]
        index_name1 = "date_index"
        fields2 = ["vessel_group"]
        index_name2 = "vessel_group_index"
        arcpy.management.AddIndex(track, fields1, index_name1)
        arcpy.management.AddIndex(track, fields2, index_name2)


add_attribute_index()