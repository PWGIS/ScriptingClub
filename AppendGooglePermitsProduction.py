#2345678901234567890123456789012345678901234567890123456789012345678901234567890
#        1         2         3         4         5         6         7         8
# -----------------------------------------------------------------------------

#                                 GooglePermits.py
#
# PURPOSE:
#
# Automate the process of adding google boundaries, fiber, and structures into the SDE layers from a layer package
# sent to us by the engineers.  Before running the script you need to have created a folder for each new layer package.
# The folder should be named with the permitID and placed inside the New folder found within F:\GIS\UtilityPermits\GOOGLE.
# The script is essentially a giant For loop through the New folder.
#
# 1).  Create a file geodatabase on your C drive and download the current google feature dataset into the gdb.
#
# 2).  Loop through the permit folders inside the New folder and for each permit folder we do the following.
#
#       a).  Set the variable PermitID equal to the folder name.  So if the folder is named "16-1023" the value
#            of the variable PermitID is 16-0123.
#
#       b).  Once the PermitID is known you make that the active directory.
#
#       c).  Determine the name of the layer package inside the folder and then rename it so it matches the permitID.
#
#       d).  Extract the layer package to the Google folder located at C:\Temp.
#
# 3).  For each permit folder on the C drive, walk the folder structure looking for file geodatabases.  If you find one
#      create a folder called "shapefiles" and then convert the feature classes we need into shapefiles and place
#      them in the shapefile folder.  Only do this for the first file geodatabase.  This is because additional gdbs are
#      simply duplicates of the first one.
#
# 4).  Create a version then loop through the permit folders and using the Select by Attributes tool delete any existing features
#      associated with the permits/
#
# 5).  Walk the file structure to find features that need to be added to the appropriate sde feature class.  Use the append tool
#      to append the polygon, line, and point features.
#
# 6).  Use the Select by Attribute and Calculate Features tools to calculate the PermitID for the selected features.
#      (Remember the variable PermitID was assigned a value in the second step.)
#
# 7).  Move the permit folder from the New folder to the main GOOGLE folder.  Delete the permit folder on the C drive.
#
# 8).  Go on to the next folder and repeat steps 3) through 7).
#
# 9).  Reconcile and post.
#-----------------------------------------------------------------------------
#
# DEPENDENCIES:
#
# 1).  ArcMap 10.1 or higher.
#
# 2).  Within the C:\TEMP folder a connection to the your version of PW.
#
# 3).  A folder named "New" located here: F:\GIS\UtilityPermits\GOOGLE.
#
# 4).  New Google layer packages need to be placed in a folder named from the permitID.  These new permit folder are placed inside the New folder.
#
# 5).  A folder named "Google" inside C:\TEMP.
#
# -----------------------------------------------------------------------------
# INPUT(S):
#
# 1). 
#
# 
# -----------------------------------------------------------------------------
# OUTPUT(S):
#
# 1). 
#
# -----------------------------------------------------------------------------
# TODO ITEMS (in no particular order)
# 1).  Need to get rid of the for loop in FolderExtraction function because it is not needed.
#
# 2).  
# -----------------------------------------------------------------------------
# INSTALLATION INSTRUCTIONS:
#
# Here is what the command should look like when used with "Schedule Tasks":
#  
# Running under Windows 7, use the "Task Scheduler" to schedule this script
# to run at night (it currently runs at 9:00PM).  The scheduler calls a DOS
# batch script which in turn runs this python script.  The batch script is used
# to redirect the messages to a log file as follows:
#
# .\AUTOID.py >> autoid.log  2>&1
# -----------------------------------------------------------------------------
# HISTORY:
#
# (20161013-doig): Initial coding
# (20161108-eno): Coding for Create GDB & Copy Features
# (20161130-eno): Combined CreateVersion() within CreateFeatures() due to the functions not being able to run seperately,
#                 causing a disconnect during the append task. Version name currently will be todayhhmm format due to the fact
#                 that if the script were to crash the version would need to be created again. Having HHMM would prevent you from
#                 having to delete the version before re-running the script.
# (20161212-eno): Started to recieve permit revisions. We added a section under the ##CreateFeatures() function to search for
#                 existing features based on the permitID and delete them before the append.
# (20161222-doig): Code added to deal with file geodatabases.  Changed the for loop to a os.walk so that we walk the entire
#                  file structure looking for the needed shapefiles (which the contractors are hiding in increasingly obscure places.)
# ==============================================================================
# Import arcpy module
import arcpy, sys, string, os, time, shutil, tempfile

arcpy.env.overwriteOutput = True

today=time.strftime("%Y%m%d", time.localtime())
todayhhmm = time.strftime("%Y%m%dT%H%M", time.localtime())

def LogMessage( message):
    print (todayhhmm + message)
    return

# Global variables:
NewFolder = "F:/GIS/UtilityPermits/GOOGLE"  ##where all the layer packages are stored inside individual folders named with the PermitID
NewPermitFolder = "F:/GIS/UtilityPermits/GOOGLE/New"  ##a newly created folder where new (unprocessed) layer packages are stored.  Again inside a folder named with the PermitID
Google = "C:/TEMP/Google"  ##Folder where the extracted files from the layer package are saved
versionName = "Google" + todayhhmm
##GoogleBoundary = "C:/TEMP/PW_Seando.sde/PW.PW.Google/PW.PW.GoogleBoundary"
##GoogleFiber = "C:/TEMP/PW_Seando.sde/PW.PW.Google/PW.PW.GoogleFiber"
##GoogleStructure = "C:/TEMP/PW_Seando.sde/PW.PW.Google/PW.PW.GoogleStructure"
##inWorkspace = "C:/TEMP/PW_Seando.sde"
##parentVersion = "PW.PermitsSeando"
GoogleBoundary = "C:/TEMP/PW_Erikaki.sde/PW.PW.Google/PW.PW.GoogleBoundary"
GoogleFiber = "C:/TEMP/PW_Erikaki.sde/PW.PW.Google/PW.PW.GoogleFiber"
GoogleStructure = "C:/TEMP/PW_Erikaki.sde/PW.PW.Google/PW.PW.GoogleStructure"
inWorkspace = "C:/TEMP/PW_Erikaki.sde"
parentVersion = "PW.PermitsErikaki"

def MakeGDB():
    LogMessage ("*******************************************************************")
    LogMessage(" Geodatabase creation...")
    FileGDBName="Google" + today
    OutputLocation= "C:/TEMP"  
    arcpy.CreateFileGDB_management(OutputLocation, FileGDBName)
    # Set workspace
    arcpy.env.workspace="C:/TEMP/Google/Google" + today + ".gdb"
    LogMessage(" Geodatabase created")
    LogMessage( FileGDBName + "/GoogleBoundary_CopyFeatures")
    arcpy.Copy_management(GoogleBoundary,"C:/TEMP/Google" + today + ".gdb/" +"Google_Boundary")
    LogMessage( FileGDBName + "/GoogleFiber_CopyFeatures")
    arcpy.Copy_management(GoogleFiber,"C:/TEMP/Google" + today + ".gdb/" +"Google_Fiber")
    LogMessage( FileGDBName + "/GoogleStructure_CopyFeatures")
    arcpy.Copy_management(GoogleStructure,"C:/TEMP/Google" + today + ".gdb/" +"Google_Structures")
    LogMessage ("Copy is good!")                
    return                 
    
##Run through the permit folders in the "NEW" folder, create a new folder in the C:/TEMP/Google folder named for
##the permit number, then extract the layer package into that folder.
def FolderExtraction():
    ##logger.info("Start the module FolderExtraction")
    LogMessage(" Start the FolderExtraction module.")        
    dirs = os.listdir(NewPermitFolder)
    ##loop through all the folders found in the "New" folder
    for file in dirs:
        try:
            LogMessage( file)
            ##set the variable PermitID to the name of the folder.  The folder is named after the permitID (must be done manually before running script).
            PermitID = file
            ##once the PermitID is set you make that folder the active directory
            os.chdir(NewPermitFolder + "/" + PermitID)
            ##the permit folder actually only contains one file (a layer file) so I probably don't have to do a For loop here.  Basically I just need
            ##code that would go into the permit folder and extract the layer package to C:\TEMP\Google.  What it currently does is loop through the
            ##permit folder, renames the layer package so it has the PermitID as its name and then extracts it to C:\TEMP\Google.  I rename it because
            ##you have to provide the full path to the layer package as part of the extraction process and the layer package names are different for
            ##each submittal.
            permitdir = os.listdir(NewPermitFolder + "\\" + PermitID)
            for lpk in permitdir:
                name = lpk
                LogMessage(" " + name)
                os.rename(name, PermitID + ".lpk")
                LogMessage(" Now extract package...")
                #create folder in Google temp folder named after the PermitID
                permitFolder = Google + "/" + PermitID
                os.mkdir(permitFolder)
                arcpy.ExtractPackage_management(NewPermitFolder + "/" + PermitID + "/" + PermitID + ".lpk", permitFolder)
                LogMessage(" Package extracted...")
        except:
            LogMessage(" This package has already been extracted")
##        return
    return

##Look for file geodatabases in the permit folders you have created inside the Google folder on your C drive.  If there is one
##convert the files in it to shapefiles.  Often there are duplicate gdbs inside one permit folder so we look for the first
##gdb and only convert the feature classes in that gdb.
def ConvertGDB():
    LogMessage(" Look for file geodatabases and convert feature classes...")
    
    GoogleFolder = os.listdir(Google)
    # use the for loop here to loop through each of the permit folders.
    for tempfolders in GoogleFolder:
        LogMessage (" " + tempfolders)
        PermitID = tempfolders
        query = "CODPermitNumber = " + "'" + PermitID + "'"
        path = Google +"/" + tempfolders
        LogMessage (" This is the path: "+ path)
        # i is set to zero here so that we can use it in the os.walk code below to find only the first file gdb within a permit folder.
        i = 0

        #here you have to actually "walk" the file structure to look for geodatabases that may be hidden several levels down.
        for(path, dirs, files) in os.walk(path):
              
            for x in dirs:
                
                try:
                    fullpath = path + "/" + x
                    LogMessage(" This is the fullpath on Ln 216: " +  fullpath)
                    ##you just want it to look at the first file geodatabase because they all seem to hold duplicate data.
                    if x.endswith(".gdb") and i == 0:
                        LogMessage (" I found a geodatabase!")
                        ##make a shapefile folder where we can place the feature classes we are about to extract.
                        os.mkdir(Google +"/" + tempfolders + "/shapefiles")
##                            
                        arcpy.env.workspace = fullpath

                        ##now go through that file gdb and look for the feature classes listed below and, if found, convert them to shapefiles
                        if arcpy.Exists("Lcp_Area"):
                            arcpy.FeatureClassToShapefile_conversion(["Lcp_Area"],Google +"/" + tempfolders + "/shapefiles")  
                            LogMessage (" I found Lcp_Area!")
                        if arcpy.Exists("LCPAREA"):
                            arcpy.FeatureClassToShapefile_conversion(["LCPAREA"],Google +"/" + tempfolders + "/shapefiles")
                            LogMessage (" I found LCPAREA!")
                        if arcpy.Exists("RoughRunningLine_Buffer"):
                            arcpy.FeatureClassToShapefile_conversion(["RoughRunningLine_Buffer"],Google +"/" + tempfolders + "/shapefiles")
                            LogMessage (" I found RoughRunningLine_Buffer!")
                        if arcpy.Exists("Permit_Polygon"):
                            arcpy.FeatureClassToShapefile_conversion(["Permit_Polygon"],Google +"/" + tempfolders + "/shapefiles")
                            LogMessage (" I found Permit_Polygon!")
                        if arcpy.Exists("Permit_Application_Polygon"):
                            arcpy.FeatureClassToShapefile_conversion(["Permit_Application_Polygon"],Google +"/" + tempfolders + "/shapefiles")
                            LogMessage (" I found Permit_Application_Polygon!")
                        if arcpy.Exists("Permit_Area_Polygon"):
                            arcpy.FeatureClassToShapefile_conversion(["Permit_Area_Polygon"],Google +"/" + tempfolders + "/shapefiles")
                            LogMessage (" I found Permit_Area_Polygon!")
                        if arcpy.Exists("PermitAreaPolygon"):
                            arcpy.FeatureClassToShapefile_conversion(["PermitAreaPolygon"],Google +"/" + tempfolders + "/shapefiles")
                            LogMessage (" I found PermitAreaPolygon!")
                        if arcpy.Exists("RoughRunningLine"):
                            arcpy.FeatureClassToShapefile_conversion(["RoughRunningLine"],Google +"/" + tempfolders + "/shapefiles")
                            LogMessage (" I found RoughRunningLine!")
                        if arcpy.Exists("Structure"):
                            arcpy.FeatureClassToShapefile_conversion(["Structure"],Google +"/" + tempfolders + "/shapefiles")
                            LogMessage (" I found Structure!")
                        if arcpy.Exists("Structures"):
                            arcpy.FeatureClassToShapefile_conversion(["Structures"],Google +"/" + tempfolders + "/shapefiles")
                            LogMessage (" I found Structures!")

                        i+= 1
                except:
                    LogMessage(" Something broke!")
    
    LogMessage(" ConvertGDB Complete.")
    return

##Create a version, delete any existing features associated with the permits, and the walk the file structure to find and append any polygon,
##line, and point data into the appropriate sde feature classes.  Also calculate the appropriate attributes for each feature class.  Once those
##steps are complete, delete the permit folder from the Google folder and move on to the next folder.
def CreateFeatures():
        ##Create a version off your personal version of PW.

        arcpy.CreateVersion_management(inWorkspace, parentVersion, versionName, "PROTECTED")
        LogMessage(" version created.")
        arcpy.MakeFeatureLayer_management(GoogleBoundary, "BoundaryLayer", "", "", "")
        arcpy.MakeFeatureLayer_management(GoogleFiber, "FiberLayer", "", "", "")
        arcpy.MakeFeatureLayer_management(GoogleStructure, "StructureLayer", "", "", "")
        LogMessage(" Layers created.")
        LogMessage("Changing version to " + versionName + "...")
        arcpy.ChangeVersion_management("BoundaryLayer", "TRANSACTIONAL", "PW." + versionName, "")
        arcpy.ChangeVersion_management("FiberLayer", "TRANSACTIONAL", "PW." + versionName, "")
        arcpy.ChangeVersion_management("StructureLayer", "TRANSACTIONAL", "PW." + versionName, "")

        LogMessage(" Start the CreateFeatures module.")        
        GoogleFolder = os.listdir(Google)
        for tempfolders in GoogleFolder:
            LogMessage (" " + tempfolders)
            PermitID = tempfolders
            query = "CODPermitNumber = " + "'" + PermitID + "'"
            ##dirs = os.listdir(tempfolders)
            path = Google +"/" + tempfolders
            LogMessage (" This is the path: "+ path)
            i = 0

            # Select Layer By Attribute - Looks for existing features based on the permit
            # ID and deletes them if found, for permit revisions.  
            arcpy.SelectLayerByAttribute_management("BoundaryLayer", "NEW_SELECTION", query)
            count = int(arcpy.GetCount_management("BoundaryLayer").getOutput(0))
            # Show number of features found to be deleted.
            LogMessage (" " + str(count))
            if count > 0:
                LogMessage (str(count) + " Permits to be deleted by attribute.")
                LogMessage ("***********************I AM DELETING SOMETHING*****************************")
                arcpy.DeleteFeatures_management("BoundaryLayer")
                LogMessage (" Old Google Boundary deleted")
            else:
                LogMessage ("No features to delete")

            # Finds the fiber features that need to be deleted before appending new revision. 
            arcpy.SelectLayerByAttribute_management("FiberLayer", "NEW_SELECTION", query)
            count = int(arcpy.GetCount_management("FiberLayer").getOutput(0))
            LogMessage (" " + str(count))
            if count > 0:
                LogMessage (str(count) + " Fiber features to be deleted by attribute.")
                LogMessage ("***********************I AM DELETING SOMETHING*****************************")
                arcpy.DeleteFeatures_management("FiberLayer")
                LogMessage (" Old Google Fibers were deleted")
            else:
                LogMessage ("No features to delete")

            # Finds the structure features that need to be deleted before appending new revision. 
            arcpy.SelectLayerByAttribute_management("StructureLayer", "NEW_SELECTION", query)
            count = int(arcpy.GetCount_management("StructureLayer").getOutput(0))
            LogMessage (" " + str(count))
            if count > 0:
                LogMessage (str(count) + " Structure features to be deleted by attribute.")
                LogMessage ("***********************I AM DELETING SOMETHING*****************************")
                arcpy.DeleteFeatures_management("StructureLayer")
                LogMessage (" Old Google Structures were deleted")
            else:
                LogMessage ("No features to delete")
            

            #now walk the folder/file structure to find all the shapefiles and feature classes we need.    
            for(path, dirs, files) in os.walk(path):
                
                for x in dirs:
                    LogMessage(" " + x)
                    try:
                        fullpath = path + "/" + x
                        
                        if os.path.isfile(fullpath + "/Lcp_Area.shp") is True:
                            NewAreaPolygon = fullpath + "/Lcp_Area.shp"
                            LogMessage(" Lcp_Area Found") ##shapefile that includes the GoogleBoundary for this PermitID
                            arcpy.Append_management(NewAreaPolygon, "BoundaryLayer", "NO_TEST")
                            LogMessage(" Google boundary append complete")
                            
                        elif os.path.isfile(fullpath + "/Permit_Area_Polygon.shp") is True:
                            NewAreaPolygon = fullpath + "/Permit_Area_Polygon.shp"
                            LogMessage(" Permit_Area_Polygon found") ##shapefile that includes the GoogleBoundary for this PermitID
                            arcpy.Append_management(NewAreaPolygon, "BoundaryLayer", "NO_TEST")
                            LogMessage(" Google boundary append complete")
                            
                        elif os.path.isfile(fullpath + "/PermitAreaPolygon.shp") is True:
                            NewAreaPolygon = fullpath + "/PermitAreaPolygon.shp"
                            LogMessage(" PermitAreaPolygon found") ##shapefile that includes the GoogleBoundary for this PermitID
                            arcpy.Append_management(NewAreaPolygon, "BoundaryLayer", "NO_TEST")
                            LogMessage(" Google boundary append complete")
                            
                        elif os.path.isfile (fullpath + "/Lcp.shp") is True:
                            NewAreaPolygon = fullpath + "/Lcp.shp"
                            LogMessage(" Lcp Found") ##shapefile that includes the GoogleBoundary for this PermitID
                            arcpy.Append_management(NewAreaPolygon, "BoundaryLayer", "NO_TEST")
                            LogMessage(" Google boundary append complete")
                            
                        elif os.path.isfile (fullpath + "/LCPAREA.shp") is True:
                            NewAreaPolygon = fullpath + "/LCPAREA.shp"
                            LogMessage(" LCPAREA found") ##shapefile that includes the GoogleBoundary for this PermitID
                            arcpy.Append_management(NewAreaPolygon, "BoundaryLayer", "NO_TEST")
                            LogMessage(" Google boundary append complete")
                            
                        elif os.path.isfile (fullpath + "/RoughRunningLine_Buffer.shp") is True:
                            NewAreaPolygon = fullpath + "/RoughRunningLine_Buffer.shp"
                            LogMessage(" RoughRunningLine_Buffer Found") ##shapefile that includes the GoogleBoundary for this PermitID
                            arcpy.Append_management(NewAreaPolygon, "BoundaryLayer", "NO_TEST")
                            LogMessage(" Google boundary append complete")
                                
                        elif os.path.isfile (fullpath + "/Permit_Polygon.shp") is True:
                            NewAreaPolygon = fullpath + "/Permit_Polygon.shp"
                            LogMessage(" Permit_Polygon Found") ##shapefile that includes the GoogleBoundary for this PermitID
                            arcpy.Append_management(NewAreaPolygon, "BoundaryLayer", "NO_TEST")
                            LogMessage(" Google boundary append complete")

                        elif os.path.isfile (fullpath + "/PermitPolygon.shp") is True:
                            NewAreaPolygon = fullpath + "/PermitPolygon.shp"
                            LogMessage(" PermitPolygon Found") ##shapefile that includes the GoogleBoundary for this PermitID
                            arcpy.Append_management(NewAreaPolygon, "BoundaryLayer", "NO_TEST")
                            LogMessage(" Google boundary append complete")
                            
                        else:
                            LogMessage(" No boundary file found for " + PermitID) ##creates a message about the missing boundary file

                        
                        if os.path.isfile (fullpath + "/Rough_Running_Line.shp") is True:
                            NewRunningLine = fullpath + "/Rough_Running_Line.shp"  ##shapefile that includes the GoogleFiber for this PermitID
                            LogMessage(NewRunningLine)
                            arcpy.Append_management(NewRunningLine, "FiberLayer", "NO_TEST")
                            LogMessage(" Google fiber append complete!")
                                
                        elif os.path.isfile (fullpath + "/RoughRunningLine.shp") is True:
                            NewRunningLine = fullpath + "/RoughRunningLine.shp"  ##shapefile that includes the GoogleFiber for this PermitID
                            LogMessage(NewRunningLine)
                            arcpy.Append_management(NewRunningLine, "FiberLayer", "NO_TEST")
                            LogMessage(" Google fiber append complete!")
                            
                        else:
                            LogMessage(" No google fiber layer found!")
                    
                        if os.path.isfile (fullpath + "/Structure.shp") is True:
                            NewStructure = fullpath + "/Structure.shp"  ##shapefile that includes the GoogleStructure for this PermitID
                            LogMessage(NewStructure)
                            arcpy.Append_management(NewStructure, "StructureLayer", "NO_TEST")
                            LogMessage(" Google structure append complete!")
                        elif os.path.isfile (fullpath + "/Structures.shp") is True:
                            NewStructure = fullpath + "/Structures.shp"  ##shapefile that includes the GoogleStructure for this PermitID
                            LogMessage(NewStructure)
                            arcpy.Append_management(NewStructure, "StructureLayer", "NO_TEST")
                            LogMessage(" Google structure append complete!")
                        else:
                            LogMessage(" No Structure.shp")
                    except:
                        LogMessage(" Problem with append")


            LogMessage (" Make feature layer and calculate permitID.")
            arcpy.SelectLayerByAttribute_management("BoundaryLayer", "NEW_SELECTION", "CODPermitNumber is null")
            arcpy.CalculateField_management("BoundaryLayer", "CODPermitNumber", "\"" + PermitID + "\"", "VB", "")
            link = "http://pwgis/permits/" + PermitID + ".PDF"
            arcpy.CalculateField_management("BoundaryLayer", "CODPermitLink", "\"" + link + "\"", "VB", "")
            arcpy.SelectLayerByAttribute_management("FiberLayer", "NEW_SELECTION", "CODPermitNumber is null")
            arcpy.CalculateField_management("FiberLayer", "CODPermitNumber", "\"" + PermitID + "\"", "VB", "")
            arcpy.SelectLayerByAttribute_management("StructureLayer", "NEW_SELECTION", "CODPermitNumber is null")
            arcpy.CalculateField_management("StructureLayer", "CODPermitNumber", "\"" + PermitID + "\"", "VB", "")
            LogMessage(" Permit fields calculated.")

## Commenting out this section where it moves the new permit out of the New folder as well as deleting the extracted folder out of temp. 
##            shutil.move(NewPermitFolder + "/" + PermitID, NewFolder + "/" + PermitID)
##            os.chdir(Google)
##            shutil.rmtree(tempfolders)
        ##return

def Cleanup():
    LogMessage( " Start the module Cleanup")
    ## Switch back to DEFAULT version.  This is so we can delete the version.
    LogMessage("Switching back to parent version...")
    arcpy.ChangeVersion_management("BoundaryLayer", "TRANSACTIONAL", "sde.DEFAULT", "")
    arcpy.ChangeVersion_management("FiberLayer", "TRANSACTIONAL", "sde.DEFAULT", "")
    arcpy.ChangeVersion_management("StructureLayer", "TRANSACTIONAL", "sde.DEFAULT", "")
    

    ## Reconcile and post version.
    LogMessage("Reconciling/Posting version " + versionName)
    ##logFileName = "C:/TEMP/Google/GoogleLog-" + todayhhmm + ".txt"
    arcpy.ReconcileVersions_management(inWorkspace, "ALL_VERSIONS", parentVersion, "PW." + versionName,  "LOCK_ACQUIRED", "ABORT_CONFLICTS", "BY_OBJECT", "FAVOR_EDIT_VERSION", "POST", "DELETE_VERSION")
    LogMessage( "Finished")
    return


## Call the functions.
MakeGDB()
FolderExtraction()
ConvertGDB()
CreateFeatures()
Cleanup()
