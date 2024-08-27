import arcpy
import os

arcpy.env.overwriteOutput = True

input_tracks = "US_Vessel_Traffic_2016_01"
input_gdb = r'E:\ArcGIS\Projects\AIS\Release_Data\Vessel_Tracks_2016.gdb'
fc_fullpath = os.path.join(input_gdb,input_tracks)
out_gdb = r'E:\Temp\monthly_split.gdb'
arcpy.env.workspace = input_gdb
aprx = arcpy.mp.ArcGISProject(r"E:\ArcGIS\Projects\AIS\AIS.aprx")
vt_map = aprx.listMaps('Vector Tile Template1')[0]

for fc in arcpy.ListFeatureClasses(input_tracks):
    arcpy.analysis.SplitByAttributes(fc_fullpath, out_gdb, 'vessel_group')

arcpy.env.workspace = out_gdb
vessel_group_list = ['Cargo', 'Fishing', 'Military', 'Not_Available', 'Other', 'Passenger', 'Pleasure', 'Tanker', 'Tow']
for vessel_group in vessel_group_list:
    arcpy.management.Rename(
        in_data=os.path.join(out_gdb,vessel_group),
        out_data=os.path.join(out_gdb,(input_tracks + "_" + vessel_group)),
        data_type="FeatureClass"
        )
    arcpy.management.Delete(in_data=os.path.join(out_gdb,vessel_group))

for fc in arcpy.ListFeatureClasses(str(input_tracks + "*")):
    arcpy.management.CreateVectorTileIndex(
    in_map=vt_map,
    out_featureclass=r"E:\Temp\vector_tile.gdb\US_Vessel_Traffic_2016_01_Tow_vti",
    service_type="ONLINE",
    tiling_scheme=None,
    vertex_count=1000
)