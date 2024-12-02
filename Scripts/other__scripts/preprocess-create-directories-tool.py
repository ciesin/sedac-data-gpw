# un-adjustment.py
# set up preprocessing folders
# Kytt MacManus
# 6-6-13

# import libraries
import os, arcpy, sys
import datetime

# set counter
startTime = datetime.datetime.now()

# define input ISO
iso = arcpy.GetParameterAsText(0)
# define preprocessing workspace
workspace = r'\\Dataserver0\gpw\GPW4\Preprocessing\Country'
arcpy.env.workspace = workspace
scratch = arcpy.env.scratchFolder
# check if directory already exists, if it does exit
newDir = workspace + os.sep + iso
if arcpy.Exists(newDir):
    sys.exit("Directory already exists")
else:
    # create iso directory
    arcpy.CreateFolder_management(workspace,iso)
    # create ingest and match folders
    root = workspace + os.sep + iso
    arcpy.CreateFolder_management(root,"Ingest")
    ingest = root + os.sep + "Ingest"
    arcpy.CreateFolder_management(root,"Match")
    match = root + os.sep + "Match"
    # create ingest sub-directories
    arcpy.CreateFolder_management(ingest,"Census")
    ingestCensus = ingest + os.sep + "Census"
    arcpy.CreateFolder_management(ingest,"Boundary")
    ingestBoundary = ingest + os.sep + "Boundary"
    print "Created folder structure"
    arcpy.AddMessage("Created folder structure")
    # create file geodatabases
    gadm2GDB = scratch + os.sep + "gadm2.gdb"
    if arcpy.Exists(gadm2GDB):
        arcpy.Delete_management(gadm2GDB)
    else:
        pass
    arcpy.CreateFileGDB_management(scratch,"gadm2")
    arcpy.CreateFileGDB_management(ingestBoundary,"boundary_adjustment")
    arcpy.CreateFileGDB_management(match,iso + "_match")
    ### create personal geodatabases
    arcpy.CreatePersonalGDB_management(ingestCensus,iso + "_ingest")
    arcpy.CreatePersonalGDB_management(match,iso + "_match_access")
    print "Created file GDBs"
    arcpy.AddMessage("Created file GDBs")
    # check the gadm country data to determine its administrative level
    gadmAdminWS = r'\\Dataserver0\gpw\GPW4\Preprocessing\Global\AdministrativeBoundaries'
    gadmFeatures = gadmAdminWS + os.sep + "gadm2_country.gdb" + os.sep + iso
    fields = ["ID_0", "ID_1", "ID_2", "ID_3", "ID_4", "ID_5"]
    searchRows = arcpy.da.SearchCursor(gadmFeatures,fields)
    for row in searchRows:
        if row[1] == None:
            suffix = "0"
            break
        elif row[2] == None:
            suffix = "1"
            break
        elif row[3] == None:
            suffix = "2"
            break
        elif row[4] == None:
            suffix = "3"
            break
        elif row[5] == None:
            suffix = "4"
            break
        elif row[5] <> None:
            suffix = "5"
            break
    del row
    del searchRows
    print "The gadm country file is at admin: " + suffix
    arcpy.AddMessage("The gadm country file is at admin: " + suffix)
        

    # copy GADM files in the gadm2 gdb
    arcpy.CopyFeatures_management(gadmAdminWS + os.sep + "gadm2_admin0.gdb" + os.sep + iso,
                                  gadm2GDB + os.sep + iso + "_admin0")
    arcpy.CopyFeatures_management(gadmAdminWS + os.sep + "gadm2_country.gdb" + os.sep + iso,
                                  gadm2GDB + os.sep + iso + "_admin" + suffix)
    # Copy gdb
    arcpy.Copy_management(gadm2GDB,ingestBoundary + os.sep + "gadm2.gdb")

        
print datetime.datetime.now() - startTime  
