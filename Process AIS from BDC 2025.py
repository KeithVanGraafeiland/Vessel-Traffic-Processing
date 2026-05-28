import arcpy
from datetime import datetime
import os
import zipfile

import arcpy.management

arcpy.env.overwriteOutput = True
## Tested in ArcGIS Pro 2.8.2 (Released)

#ROOT = "C:/Users/keit8223/Documents/ArcGIS/Projects/AIS/AIS Processing/"
ROOT = r'D:\Temp\AIS\processing'
filtered_dir = os.path.join(ROOT, 'Filtered')
YEAR = 2025
# Define Variables
#input_MFC = r"C:\Users\keit8223\Documents\ArcGIS\Projects\AIS\AIS_2020.bdc\AIS_2020"
mfc_file = os.path.join(ROOT, 'AIS_ProProject', 'AIS_MFC.mfc')
# input_MFC = os.path.join(mfc_file, 'AIS_' + str(YEAR) + '_RAW')
input_filtered_MFC = os.path.join(mfc_file, 'AIS_' + str(YEAR) + '_Filtered')
out_tracks_gdb = os.path.join(filtered_dir, 'Reconstruct_Tracks_Out.gdb')
#out_filtered_tracks_gdb = os.path.join(filtered_dir, 'Reconstruct_Filtered_Tracks_Out.gdb')
# out_tracks = os.path.join(out_tracks_gdb, 'US_Vessel_Traffic_' + str(YEAR))
out_filtered_tracks = os.path.join(out_tracks_gdb, 'US_Vessel_Traffic_' + str(YEAR) + '_filtered')
start_date = "7/1/" + str(YEAR)

# Define Constants (should use uppercase for constants ex: TRACK_FIELDS

# TRACK_FIELDS = 'MMSI;VesselName;IMO;VesselType;Length;Width;Draft;TransceiverClass'
#TRACK_FIELDS = 'MMSI;VesselName;IMO;VesselType;Length;Width;Draft;TranscieverClass'
TRACK_FIELDS = 'MMSI;Vessel_Name;IMO;Vessel_Type;Length;Width;Draft'
VESSEL_TYPE_INFO = os.path.join(ROOT, 'AIS_ProProject', 'Vessel_Traffic_Schema.gdb','VesselType_Codes')
# YEARLY_GDB = os.path.join(ROOT, 'Yearly_Vessel_Tracks.gdb')
YEARLY_filtered_GDB = os.path.join(filtered_dir, 'Yearly_Vessel_Tracks_Filtered.gdb')
# MONTHLY_GDB = os.path.join(ROOT, 'Monthly_Vessel_Tracks.gdb')
MONTHLY_filtered_GDB = os.path.join(filtered_dir, 'Monthly_Vessel_Tracks_Filtered.gdb')
TRACK_SCHEMA = os.path.join(ROOT, "AIS_ProProject",'Vessel_Traffic_Schema.gdb', 'Vessel_Tracks_Schema')
# TRACK_NAME = os.path.split(out_tracks)[1]
filtered_TRACK_NAME = os.path.split(out_filtered_tracks)[1]
# TRACK_YEAR = TRACK_NAME.split("_")[3]
filtered_TRACK_YEAR = filtered_TRACK_NAME.split("_")[3]
# YEAR_NAME = 'US_Vessel_Traffic_' + TRACK_YEAR
filtered_YEAR_NAME = 'US_Vessel_Traffic_' + filtered_TRACK_YEAR
# MONTHLY_TRACKS_FOLDER = os.path.join(ROOT, 'Monthly_Products')
monthly_filtered_TRACKS_FOLDER = os.path.join(filtered_dir, 'Monthly_Products_Filtered')
# CLEAN_TRACKS = os.path.join(YEARLY_GDB, YEAR_NAME)
filtered_CLEAN_TRACKS = os.path.join(YEARLY_filtered_GDB, filtered_YEAR_NAME)

# if not os.path.exists(filtered_dir):
#     os.makedirs(filtered_dir)

if not os.path.exists(filtered_dir):
    os.makedirs(filtered_dir)

if not os.path.exists(out_tracks_gdb):
    arcpy.management.CreateFileGDB(filtered_dir, os.path.basename(out_tracks_gdb), out_version='CURRENT')
# if not os.path.exists(out_filtered_tracks_gdb):
#     arcpy.management.CreateFileGDB(filtered_dir, os.path.basename(out_filtered_tracks_gdb), out_version='CURRENT')

# if not os.path.exists(YEARLY_GDB):
#     arcpy.management.CreateFileGDB(ROOT, os.path.basename(YEARLY_GDB), out_version='CURRENT')
if not os.path.exists(YEARLY_filtered_GDB):
    arcpy.management.CreateFileGDB(filtered_dir, os.path.basename(YEARLY_filtered_GDB), out_version='CURRENT')


# if not os.path.exists(MONTHLY_GDB):
#     arcpy.management.CreateFileGDB(ROOT, os.path.basename(MONTHLY_GDB), out_version='CURRENT')
if not os.path.exists(MONTHLY_filtered_GDB):
    arcpy.management.CreateFileGDB(filtered_dir, os.path.basename(MONTHLY_filtered_GDB), out_version='CURRENT')

# if not os.path.exists(MONTHLY_TRACKS_FOLDER):
#     os.makedirs(MONTHLY_TRACKS_FOLDER)
if not os.path.exists(monthly_filtered_TRACKS_FOLDER):
    os.makedirs(monthly_filtered_TRACKS_FOLDER)

def log(message):
    print(message,datetime.now())

def process_tracks():
    log("-----INITIALIZING RECONSTRUCT TRACKS-----")
    arcpy.gapro.RefreshBDC(mfc_file)
    # with arcpy.EnvManager(outputCoordinateSystem='PROJCS["WGS_1984_Web_Mercator_Auxiliary_Sphere",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],'
    #                                          'PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Mercator_Auxiliary_Sphere"],PARAMETER["False_Easting",0.0],'
    #                                          'PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",0.0],PARAMETER["Standard_Parallel_1",0.0],PARAMETER["Auxiliary_Sphere_Type",0.0],'
    #                                          'UNIT["Meter",1.0]]'):
    #     arcpy.gapro.ReconstructTracks(input_MFC, out_tracks, TRACK_FIELDS, "GEODESIC", '', None, None, "30 Minutes", "1 Miles", "1 Days", start_date, "SOG MEAN;COG MEAN;Heading MEAN", None, "GAP")
    with arcpy.EnvManager(outputCoordinateSystem='PROJCS["WGS_1984_Web_Mercator_Auxiliary_Sphere",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],'
                                            'PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Mercator_Auxiliary_Sphere"],PARAMETER["False_Easting",0.0],'
                                            'PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",0.0],PARAMETER["Standard_Parallel_1",0.0],PARAMETER["Auxiliary_Sphere_Type",0.0],'
                                            'UNIT["Meter",1.0]]'):
        arcpy.gapro.ReconstructTracks(input_filtered_MFC, out_filtered_tracks, TRACK_FIELDS, "GEODESIC", '', None, None, "30 Minutes", "1 Miles", "1 Days", start_date, "SOG MEAN;COG MEAN;Heading MEAN", None, "GAP")
    log("-----COMPLETED RECONSTRUCT TRACKS-----")

def manage_attributes():
    log("-----INITIALIZING ATTRIBUTE MANAGEMENT-----")
    VESSEL_TYPE = "vessel_type"
    log("Managing field names.....")
    # arcpy.management.AlterField(out_tracks, "VesselName", "vessel_name", "vessel name")
    arcpy.management.AlterField(out_filtered_tracks, "Vessel_Name", "vessel_name", "vessel name")
    # arcpy.management.AlterField(out_tracks, "VesselType", VESSEL_TYPE, "vessel type")
    arcpy.management.AlterField(out_filtered_tracks, "Vessel_Type", VESSEL_TYPE, "vessel type")
    # arcpy.management.AlterField(out_tracks, "TransceiverClass", "transceiver_class", "transceiver class")
    # arcpy.management.AlterField(out_tracks, "COUNT", "vertices", "vertices")
    arcpy.management.AlterField(out_filtered_tracks, "COUNT", "vertices", "vertices")



    log("Joining vessel group and vessel class fields using vessel type codes.....")
    # arcpy.management.JoinField(out_tracks, VESSEL_TYPE, VESSEL_TYPE_INFO, VESSEL_TYPE, ["vessel_group", "vessel_class"])
    arcpy.management.JoinField(out_filtered_tracks, VESSEL_TYPE, VESSEL_TYPE_INFO, VESSEL_TYPE, ["vessel_group", "vessel_class"])

    log("Assign Other to NULL values for vessel group.....")
    # arcpy.management.CalculateField(out_tracks, "vessel_group", '"Other" if !'+VESSEL_TYPE+'! is None else !vessel_group!',
    #                                 "PYTHON3", '', "TEXT", "NO_ENFORCE_DOMAINS")
    arcpy.management.CalculateField(out_filtered_tracks, "vessel_group", '"Other" if !'+VESSEL_TYPE+'! is None else !vessel_group!',
                                    "PYTHON3", '', "TEXT", "NO_ENFORCE_DOMAINS")
    log("Assign Other to NULL values for vessel class.....")
    # arcpy.management.CalculateField(out_tracks, "vessel_class", '"Other" if !'+VESSEL_TYPE+'! is None else !vessel_class!',
    #                                 "PYTHON3", '', "TEXT", "NO_ENFORCE_DOMAINS")
    arcpy.management.CalculateField(out_filtered_tracks, "vessel_class", '"Other" if !'+VESSEL_TYPE+'! is None else !vessel_class!',
                                    "PYTHON3", '', "TEXT", "NO_ENFORCE_DOMAINS")
    log("Adding date attributes for month and day.....")
    # arcpy.ca.AddDateAttributes(out_tracks, "END_DATE", "MONTH month;DAY_OF_MONTH day")
    arcpy.ca.AddDateAttributes(out_filtered_tracks, "END_DATE", "MONTH month;DAY_OF_MONTH day")
    log("-----COMPLETED ATTRIBUTE MANAGEMENT-----")

def optimize_tracks():
    log("-----INITIALIZING TRACK OPTIMIZATION-----")
    log("Creating empty feature class for tracks.....")
    # arcpy.CreateFeatureclass_management(YEARLY_GDB, YEAR_NAME, "POLYLINE",
    #                                     TRACK_SCHEMA, "DISABLED", "DISABLED")
    arcpy.CreateFeatureclass_management(YEARLY_filtered_GDB, filtered_YEAR_NAME, "POLYLINE",
                                    TRACK_SCHEMA, "DISABLED", "DISABLED")
    log("Appending tracks to empty feature class.....")
    # arcpy.management.Append(out_tracks, CLEAN_TRACKS, "NO_TEST")
    arcpy.management.Append(out_filtered_tracks, filtered_CLEAN_TRACKS, "NO_TEST")

    log("Defining projection on tracks.....")
    # arcpy.management.DefineProjection(CLEAN_TRACKS, 'PROJCS["WGS_1984_Web_Mercator_Auxiliary_Sphere",'
    #                                                 'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],'
    #                                                 'PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Mercator_Auxiliary_Sphere"],'
    #                                                 'PARAMETER["False_Easting",0.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",0.0],'
    #                                                 'PARAMETER["Standard_Parallel_1",0.0],PARAMETER["Auxiliary_Sphere_Type",0.0],UNIT["Meter",1.0]]')
    arcpy.management.DefineProjection(filtered_CLEAN_TRACKS, 'PROJCS["WGS_1984_Web_Mercator_Auxiliary_Sphere",'
                                                    'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],'
                                                    'PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Mercator_Auxiliary_Sphere"],'
                                                    'PARAMETER["False_Easting",0.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",0.0],'
                                                    'PARAMETER["Standard_Parallel_1",0.0],PARAMETER["Auxiliary_Sphere_Type",0.0],UNIT["Meter",1.0]]')
    log("-----COMPLETED TRACK OPTIMIZATION-----")

def create_products():
    log("-----INITIALIZING PRODUCT GENERATION-----")
    log("Creating value list.....")
    valueList = []  # array to hold list of values collected
    valueSet = set()  # set to hold values to test against to get list
    rows = arcpy.SearchCursor(filtered_CLEAN_TRACKS)
    field = "month"
    for row in rows:
        value = row.getValue(field)
        if value not in valueSet:
            valueList.append(value)
            valueSet.add(value)
    valueList.sort()
    log("Done creating value list.....")

    log("Beginning to create monthly tracks.....")
    for x in valueList:
        xname = f"{x:02d}"
        # out_FC = MONTHLY_GDB + "\\" + YEAR_NAME + "_" + xname
        out_filtered_FC = MONTHLY_filtered_GDB + "\\" + filtered_YEAR_NAME + "_" + xname
        # out_FC_month = YEAR_NAME + "_" + xname
        out_filtered_FC_month = filtered_YEAR_NAME + "_" + xname
        where_clause = "\"month\" = " + str(x)
        gdbFile = monthly_filtered_TRACKS_FOLDER + "\\" + out_filtered_FC_month + ".gdb"
        monthly_fc = gdbFile + "\\" + out_filtered_FC_month
        outFile = gdbFile[0:-4] + '.zip'
        gdbName = os.path.basename(gdbFile)
        log("Selecting tracks for " + out_filtered_FC_month)
        arcpy.analysis.Select(filtered_CLEAN_TRACKS, out_filtered_FC, where_clause)
        log("Creating monthly file geodatabase for " + out_filtered_FC_month)
        arcpy.management.CreateFileGDB(monthly_filtered_TRACKS_FOLDER, out_filtered_FC_month)
        log("Creating monthly feature class for " + out_filtered_FC_month)
        arcpy.management.CopyFeatures(out_filtered_FC,monthly_fc)
        log("Creating zip file for " + out_filtered_FC_month)
        with zipfile.ZipFile(outFile, mode='w',
                             compression=zipfile.ZIP_DEFLATED,
                             allowZip64=True) as myzip:
            for f in os.listdir(gdbFile):
                if f[-5:] != '.lock':
                    myzip.write(os.path.join(gdbFile, f), gdbName + '\\' + os.path.basename(f))
        log("Done creating zip file for " + out_filtered_FC_month)
    log("Done creating monthly tracks.....")
    log("-----COMPLETED PRODUCT GENERATION-----")


log("********** PROCESS AIS FROM BIG DATA CONNECTION **********")
start_time = datetime.now()
process_tracks()
manage_attributes()
optimize_tracks()
create_products()
time_elapsed = datetime.now() - start_time
print('Time elapsed (hh:mm:ss.ms) {}'.format(time_elapsed))
log("********** PROCESS AIS FROM BIG DATA CONNECTION **********")
