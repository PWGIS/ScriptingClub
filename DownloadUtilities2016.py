#
# 2345678901234567890123456789012345678901234567890123456789012345678901234567890
#        1         2         3         4         5         6         7         8
# -----------------------------------------------------------------------------

#                                 DownloadUtilities2016.py
#
# PURPOSE:
#
# Download stormwater, sanitary sewer, and water features and pipes data.
#
#
# 1).  A folder named "Utilities" is created in the existing TEMP folder on the C drive.
#      This functiononly needs to be run the very first time you create the script.
#      (Alternatively you can just create a folder inside of the TEMP folder and skip
#      ever running the first function.)  Any geodatabase you create with this script
#      will be created inside the "Utilities" folder.

# 2).  A file geodatabase is created on the local system(currently in
#      "C:/TEMP/Utilities"). The naming convention for the file geodatabase is
#      "Utilities<YYYYMMDD>" where "<YYYYMMDD>" is the four digit year (YYYY),
#      two digit month (MM), and two digit day (DD).
#
# 2).  The three pipe feature classes for water (wnWaterMain, wnForceMain, and
#      wnGravity), three pipe feature classes for sewer (snForceMain, snGravity,
#      and snLateralLine), and the swPipes layer for stormwater are copied to
#      this local geodatabase.
#
#

# -----------------------------------------------------------------------------
#
# DEPENDENCIES:
#
# 1).  ArcMap 10.1 or higher.
#
# 2).  A database connection to A1 server.
#
#
#
# -----------------------------------------------------------------------------
# INPUT(S):
#
# 1). Layers from the Sewer, StormWater, and Water feature datasets.
#
#
# -----------------------------------------------------------------------------
# OUTPUT(S):
#
# 1). See Purpose above for Outputs.
#
# -----------------------------------------------------------------------------
# NOTES:
#
#
#
# TODO ITEMS (in no particular order)
# 1).  Set as a scheduled task.
# 2).
#
# -----------------------------------------------------------------------------
# INSTALLATION INSTRUCTIONS:
#
# From SeanM's autoid.py file:
# Running under Windows 7, use the "Task Scheduler" to schedule this script
# to run at night (it currently runs at 9:00PM).  The scheduler calls a DOS
# batch script which in turn runs this python script.  The batch script is used
# to redirect the messages to a log file as follows:
#
# .\AUTOID.py >> autoid.log  2>&1
#
# -----------------------------------------------------------------------------
# HISTORY:
#
# (20161011-doig): Initial coding complete

# ==============================================================================
#

# Import arcpy and other modules
#import arcpy, sys, string, os, time, shutil
import arcpy, time, os

# The next line means that when running the arcpy tools any outputs will overwrite existing outputs
arcpy.env.overwriteOutput = True

# the next two lines create two global variables that are used later in the script
today=time.strftime("%Y%m%d", time.localtime())
todayhhmm = time.strftime("%Y%m%dT%H%M", time.localtime())

# the LogMessage function is used throughout the script to add the time to any print statements
def LogMessage( message):
    print time.strftime ("%Y-%m-%dT%H:%M:%S ", time.localtime()) + message

    return

# variables specific  to this script
# very importantly the listed database connection MUST match the name you have given it.  So change the portion
# of the variable names below from "A1-DurhamGIS" to match what you have in ArcCatalog.
##StormWater = "Database Connections/A1_durham-gis.sde/gis_data.A1.StormWater"  #feature dataset
##SewerSystem = "Database Connections/A1_durham-gis.sde/gis_data.A1.SewerSystem"  #feature dataset
WaterSystem = "Database Connections/A1_durham-gis.sde/gis_data.A1.WaterSystem" #feature dataset
##Impervious = "Database Connections/A1_durham-gis.sde/gis_data.A1.Impervious_Area/gis_data.A1.ImperviousArea"

#Location where the file geodatabases will be created.  The first function below creates the folder "Utilities".
UtilitiesDIR = "C:/TEMP/Utilities"



# Set workspace the variable thisWorkspace can be used wherever the workspace needs to be indicated.
arcpy.Workspace = "C:/TEMP/Utilities/Utilities" + today + ".gdb"
thisWorkspace = arcpy.Workspace

# Make the folder where the file geodatabases will be created.  You only do this the very first time you run the script.
def MakeBuildDirectory():
    LogMessage(" MakeBuildDirectory...")
    os.mkdir(UtilitiesDIR)
    os.chdir(UtilitiesDIR)
    LogMessage(" MakeBuildDirectory Complete.")
    return

# Create a file geodatabase.  Each time you create it the program appends the current date on to the end of the name.
def MakeGDB():
    LogMessage(" Geodatabase creation...")
    FileGDBName = "Utilities" + today  #The variable for the geodatabase name
    #OutputLocation = UtilitiesDIR

    arcpy.CreateFileGDB_management(UtilitiesDIR, FileGDBName)
    LogMessage(" Geodatabase created")
    return

# Copy the feature classes/datasets into today's file geodatabase.
def CopyFeatures():
    LogMessage(" Copy feature datasets...")

##    arcpy.Copy_management(SewerSystem, thisWorkspace + "/SewerSystem", "FeatureDataset")
##    LogMessage(" Sewer copied.")
##    arcpy.Copy_management(StormWater, thisWorkspace + "/Stormwater", "FeatureDataset")
##    LogMessage(" Storm copied.")
    arcpy.Copy_management(WaterSystem, thisWorkspace + "/Water", "FeatureDataset")
    LogMessage(" Water copied.")
##    arcpy.Copy_management(Impervious, thisWorkspace+ "/ImperviousArea", "FeatureClass")
##    LogMessage(" Impervious copied.")

    return


# So far all you've done is write the functions.  However none of them will run UNTIL you call them below.
##MakeBuildDirectory()
MakeGDB()
CopyFeatures()
