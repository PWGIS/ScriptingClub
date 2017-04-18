#
# 2345678901234567890123456789012345678901234567890123456789012345678901234567890
#        1         2         3         4         5         6         7         8
# -----------------------------------------------------------------------------

#                                 JasonParcels.py
#
# PURPOSE:
#
# Download parcels, compare parcel to backup FGDB and select differences. 
#
#
# 1).
# 2).
# 3).  
#
#

# -----------------------------------------------------------------------------
#
# DEPENDENCIES:
#
# 1).  ArcMap 10.1 or higher.
#
# 2).  A database connection to A1 on the server. 
#
#
# -----------------------------------------------------------------------------
# INPUT(S):
#
# 1). Layers frpm parcels. 
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
# 1).  Set as a scheduled task once a week.
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
# (20170124-Eno): Initial coding

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

A1Parcel = "Database Connections/A1_durham-gis.sde/GIS_Data.A1.TaxData/gis_data.A1.Parcels"
##ParcelBackup = "C:/Work/Parcels/PID160119.gdb"
ParcelBUA1 = "C:/Work/Parcels/ParcelBU" + today + ".gdb/Parcels"
ParcelBUJ = "C:/Work/Parcels/PID160119.gdb/Parcels"

#Location where the file geodatabases will be created.
ParcelDIR = "C:/Work/Parcels"


# Set workspace the variable thisWorkspace can be used wherever the workspace needs to be indicated.
ParcelShapefiles = "C:/Work/Parcels/ParcelShapefiles"
arcpy.Workspace = "C:/Work/Parcels/ParcelBU" + today + ".gdb"
thisWorkspace = arcpy.Workspace

# Make the folder where the file geodatabases will be created.  You only do this the very first time you run the script.
def MakeBuildDirectory():
    LogMessage(" MakeBuildDirectory...")
    os.mkdir(ParcelDIR)
    os.chdir(ParcelDIR)
    LogMessage(" MakeBuildDirectory Complete.")
    return

# Create a file geodatabase.  Each time you create it the program appends the current date on to the end of the name.
def MakeGDB():
    LogMessage(" Geodatabase creation...")
    FileGDBName = "ParcelBU" + today  #The variable for the geodatabase name
    OutputLocation = ParcelDIR

    arcpy.CreateFileGDB_management(ParcelDIR, FileGDBName)
    LogMessage(" Geodatabase created")
    return

# Copy the feature classes/datasets into today's file geodatabase.
def CopyFeatures():
    LogMessage(" Copy feature datasets...")
    arcpy.Copy_management(A1Parcel, thisWorkspace+ "/ParcelBackUp", "FeatureClass")
    LogMessage(" Parcels copied.")
    return

def MakeLayers():
#Need to make feature layer before selection can happen    
    LogMessage("Making Feature Layer...")

    A1ParcelBackUp = thisWorkspace+ "/ParcelBackUp"
    ParcelBackUp_Layer = "ParcelBU_Lyr"
    ParcelsJ_Lyr = "ParcelsJ_Lyr"
  
    # Process: Make Feature Layer
    arcpy.MakeFeatureLayer_management(A1ParcelBackUp, ParcelBackUp_Layer)
    arcpy.MakeFeatureLayer_management(ParcelBUJ, ParcelsJ_Lyr)
    LogMessage("Made Features ...")
    # Process: Select Layer By Location
    arcpy.SelectLayerByLocation_management(ParcelBackUp_Layer, "ARE_IDENTICAL_TO", ParcelsJ_Lyr, "", "")
    arcpy.SelectLayerByLocation_management(ParcelBackUp_Layer,"" , "", "","SWITCH_SELECTION")
    
    arcpy.CopyFeatures_management(ParcelBackUp_Layer, "C:/Work/Parcels/ParcelShapefiles/A1ParcelDif")
    LogMessage("I did the damn thing WOO!")
    return

##MakeBuildDirectory()
MakeGDB()
CopyFeatures()
MakeLayers()

               
