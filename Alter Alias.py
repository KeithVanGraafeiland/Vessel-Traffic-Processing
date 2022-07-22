import arcpy

tracks_db = r"D:\AIS_Processing\Monthly_Vessel_Tracks.gdb"

arcpy.env.workspace = tracks_db
tracks_list = []
for fc in arcpy.ListFeatureClasses():
    tracks_list.append(fc)
print(tracks_list)

def rename_alias():
    for track in tracks_list:
        track_alias = track.replace('_', ' ')
        track_name = tracks_db + "\\" + track
        arcpy.AlterAliasName(track_name, track_alias)


rename_alias()