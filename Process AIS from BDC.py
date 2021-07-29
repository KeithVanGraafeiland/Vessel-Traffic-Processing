import arcpy
from datetime import datetime
import os
import zipfile
arcpy.env.overwriteOutput = True
import pandas as pd
from arcgis.features import GeoAccessor, GeoSeriesAccessor

# define variables
input_BDC = r"C:\Users\keit8223\Documents\ArcGIS\Projects\AIS\AIS_2020.bdc\AIS_2020_Test"
out_tracks = 'C:/Users/keit8223/Documents/ArcGIS/Projects/AIS/AIS Processing/Reconstruct_Tracks_Out.gdb/AIS_Tracks_2020_Test'
start_date = "1/1/2020"

# Constants (should use uppercase for constants ex: TRACK_FIELDS
track_fields = "MMSI;VesselName;IMO;VesselType;Length;Width;Draft;TranscieverClass"
vessel_type_info = r"C:\Users\keit8223\Documents\ArcGIS\Projects\AIS\Vessel_Traffic_Schema.gdb\VesselType_Codes"
yearly_GDB = r"C:\Users\keit8223\Documents\ArcGIS\Projects\AIS\Yearly_Vessel_Tracks.gdb"
monthly_GDB = r"C:\Users\keit8223\Documents\ArcGIS\Projects\AIS\Monthly_Vessel_Tracks.gdb"
track_schema = r"C:\Users\keit8223\Documents\ArcGIS\Projects\AIS\Vessel_Traffic_Schema.gdb\Schema_v03"
track_name = os.path.split(out_tracks)[1]
track_year = track_name.split("_")[2]
year_name = "Vessel_Tracks_" + track_year
monthly_tracks = r"C:\Users\keit8223\Documents\ArcGIS\Projects\AIS\AIS Processing\Monthly_Products"
clean_tracks = yearly_GDB + "\\" + year_name

def log(message):
    print(message,datetime.now())

def process_tracks():
    with arcpy.EnvManager(outputCoordinateSystem='PROJCS["WGS_1984_Web_Mercator_Auxiliary_Sphere",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],'
                                             'PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Mercator_Auxiliary_Sphere"],PARAMETER["False_Easting",0.0],'
                                             'PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",0.0],PARAMETER["Standard_Parallel_1",0.0],PARAMETER["Auxiliary_Sphere_Type",0.0],'
                                             'UNIT["Meter",1.0]]'):
        arcpy.gapro.ReconstructTracks(input_BDC, out_tracks, track_fields, "GEODESIC", '', None, None, "30 Minutes", "1 Miles", "1 Days", start_date, "SOG MEAN;COG MEAN;Heading MEAN", None, "GAP")
    log("End reconstruct tracks....")

def manage_attributes():
    VESSEL_TYPE = "vessel_type"
    arcpy.management.AlterField(out_tracks, "VesselName", "vessel_name", "vessel name")
    arcpy.management.AlterField(out_tracks, "VesselType", VESSEL_TYPE, "vessel type")
    arcpy.management.AlterField(out_tracks, "TranscieverClass", "transceiver_class", "transceiver class")
    arcpy.management.AlterField(out_tracks, "COUNT", "vertices", "vertices")

    arcpy.management.JoinField(out_tracks, VESSEL_TYPE, vessel_type_info, VESSEL_TYPE, ["vessel_group", "vessel_class"])

    arcpy.management.CalculateField(out_tracks, "vessel_group", '"Other" if !'+VESSEL_TYPE+'! is None else !vessel_group!',
                                    "PYTHON3", '', "TEXT", "NO_ENFORCE_DOMAINS")
    arcpy.management.CalculateField(out_tracks, "vessel_class", '"Other" if !'+VESSEL_TYPE+'! is None else !vessel_class!',
                                    "PYTHON3", '', "TEXT", "NO_ENFORCE_DOMAINS")

    arcpy.ca.AddDateAttributes(out_tracks, "END_DATE", "MONTH date_mo;DAY_OF_MONTH date_dm")

def optimize_tracks():
    arcpy.CreateFeatureclass_management(yearly_GDB, year_name, "POLYLINE",
                                        track_schema, "DISABLED", "DISABLED")

    arcpy.management.Append(out_tracks, clean_tracks, "NO_TEST")

    arcpy.management.DefineProjection(clean_tracks, 'PROJCS["WGS_1984_Web_Mercator_Auxiliary_Sphere",'
                                                    'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],'
                                                    'PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Mercator_Auxiliary_Sphere"],'
                                                    'PARAMETER["False_Easting",0.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",0.0],'
                                                    'PARAMETER["Standard_Parallel_1",0.0],PARAMETER["Auxiliary_Sphere_Type",0.0],UNIT["Meter",1.0]]')
def create_products():
    valueList = []  # array to hold list of values collected
    valueSet = set()  # set to hold values to test against to get list
    rows = arcpy.SearchCursor(clean_tracks)
    field = "date_mo"
    for row in rows:
        value = row.getValue(field)
        if value not in valueSet:
            valueList.append(value)
            valueSet.add(value)
    valueList.sort()
    log("Done getting Value List.....")

    log("Creating Monthly Tracks.....")
    for x in valueList:
        xname = f"{x:02d}"
        out_FC = monthly_GDB + "\\" + year_name + "_" + xname
        out_FC_month = year_name + "_" + xname
        where_clause = "\"date_mo\" = " + str(x)
        gdbFile = monthly_tracks + "\\" + out_FC_month + ".gdb"
        outFile = gdbFile[0:-4] + '.zip'
        gdbName = os.path.basename(gdbFile)
        arcpy.analysis.Select(clean_tracks, out_FC, where_clause)
        arcpy.management.CreateFileGDB(monthly_tracks, out_FC_month)

        with zipfile.ZipFile(outFile, mode='w',
                             compression=zipfile.ZIP_DEFLATED,
                             allowZip64=True) as myzip:
            for f in os.listdir(gdbFile):
                if f[-5:] != '.lock':
                    myzip.write(os.path.join(gdbFile, f), gdbName + '\\' + os.path.basename(f))

log("Start Processing.......")
process_tracks()
manage_attributes()
optimize_tracks()
create_products()
log("Finished Processing.......")



# # modify fields to fit schema
# now = datetime.now() # current date and time
# print("Start alter fields.....", now)
# arcpy.management.AlterField(out_tracks, "VesselName", "vessel_name", "vessel name")
# arcpy.management.AlterField(out_tracks, "VesselType", "vessel_type", "vessel type")
# arcpy.management.AlterField(out_tracks, "TranscieverClass", "transceiver_class", "transceiver class")
# arcpy.management.AlterField(out_tracks, "COUNT", "vertices", "vertices")
# now = datetime.now() # current date and time
# print("End alter fields.....", now)
#
# # Join Fields Vessel Class and Vessel Group
# now = datetime.now() # current date and time
# print("Starting join.....", now)
# arcpy.management.JoinField(out_tracks, "vessel_type", vessel_type_info, "vessel_type", ["vessel_group", "vessel_class"])
# now = datetime.now() # current date and time
# print("Join completed.....", now)
#
# # clean up null vessel type values
# now = datetime.now() # current date and time
# print("Starting null value clean-up.....", now)
# arcpy.management.CalculateField(out_tracks, "vessel_group", '"Other" if !vessel_type! is None else !vessel_group!', "PYTHON3", '', "TEXT", "NO_ENFORCE_DOMAINS")
# arcpy.management.CalculateField(out_tracks, "vessel_class", '"Other" if !vessel_type! is None else !vessel_class!', "PYTHON3", '', "TEXT", "NO_ENFORCE_DOMAINS")
# now = datetime.now() # current date and time
# print("Done null value clean-up.....", now)
#
# # print field info
# # now = datetime.now() # current date and time
# # print("Getting field info.....", now)
# # fields = arcpy.ListFields(out_tracks)
# # for field in fields:
# #     print("Field:       {0}".format(field.name))
# #     print("Alias:       {0}".format(field.aliasName))
# #     print("Type:        {0}".format(field.type))
# #     print("Is Editable: {0}".format(field.editable))
# #     print("Required:    {0}".format(field.required))
# #     print("Scale:       {0}".format(field.scale))
# #     print("Precision:   {0}".format(field.precision))
# # now = datetime.now() # current date and time
# # print("Done get field info.....", now)
#
# # add month and day of month
# now = datetime.now() # current date and time
# print("Start add date attributes.....", now)
# arcpy.ca.AddDateAttributes(out_tracks, "END_DATE", "MONTH date_mo;DAY_OF_MONTH date_dm")
# now = datetime.now() # current date and time
# # print("End add date attributes.....", now)
#
# # create empty feature class with schema to append to
# now = datetime.now() # current date and time
# # print("Creating empty feature class.....", now)
# arcpy.CreateFeatureclass_management(yearly_GDB, year_name, "POLYLINE",
#                                     track_schema, "DISABLED", "DISABLED")
# now = datetime.now() # current date and time
# print("Done creating empty feature class.....", now)
#
# # append tracks to new feature class
# now = datetime.now() # current date and time
# print("Appending to empty feature class.....", now)
# arcpy.management.Append(out_tracks, clean_tracks, "NO_TEST")
# now = datetime.now() # current date and time
# print("Finished appending to empty feature class.....", now)
#
# arcpy.management.DefineProjection(clean_tracks, 'PROJCS["WGS_1984_Web_Mercator_Auxiliary_Sphere",'
#                                               'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],'
#                                               'PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Mercator_Auxiliary_Sphere"],'
#                                               'PARAMETER["False_Easting",0.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",0.0],'
#                                               'PARAMETER["Standard_Parallel_1",0.0],PARAMETER["Auxiliary_Sphere_Type",0.0],UNIT["Meter",1.0]]')
#
# now = datetime.now() # current date and time
# print("Getting Value List.....", now)
# valueList = []  # array to hold list of values collected
# valueSet = set()  # set to hold values to test against to get list
# rows = arcpy.SearchCursor(clean_tracks)
# field = "date_mo"
# for row in rows:
#     value = row.getValue(field)
#     if value not in valueSet:
#         valueList.append(value)
#         valueSet.add(value)
# valueList.sort()
# # print(valueList)
# now = datetime.now() # current date and time
# print("Done getting Value List.....", now)
#
# print("Creating Monthly Tracks.....", now)
# for x in valueList:
#     xname = f"{x:02d}"
#     out_FC = monthly_GDB + "\\" + year_name + "_"+ xname
#     out_FC_month = year_name + "_" + xname
#     where_clause = "\"date_mo\" = " + str(x)
#     gdbFile = monthly_tracks + "\\" + out_FC_month + ".gdb"
#     outFile = gdbFile[0:-4] + '.zip'
#     gdbName = os.path.basename(gdbFile)
#     print(gdbFile)
#     arcpy.analysis.Select(clean_tracks, out_FC, where_clause )
#     arcpy.management.CreateFileGDB(monthly_tracks,out_FC_month)
#
#     with zipfile.ZipFile(outFile, mode='w',
#                          compression=zipfile.ZIP_DEFLATED,
#                          allowZip64=True) as myzip:
#         for f in os.listdir(gdbFile):
#             if f[-5:] != '.lock':
#                 myzip.write(os.path.join(gdbFile, f), gdbName + '\\' + os.path.basename(f))
#
# now = datetime.now() # current date and time
# print("Done creating Monthly Tracks.....", now)