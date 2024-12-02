# preprocess-create-directories-tool_v2.py
# set up preprocessing folders
# Kytt MacManus, edited by Erin Doxsey-Whitfield
# 14-Aug-3

# import libraries
import os, arcpy, sys
import datetime

# set counter
startTime = datetime.datetime.now()

# define input ISO
##isoText = arcpy.GetParameterAsText(0)
isoText = "SOM"
iso = isoText.upper()

# define preprocessing workspace
workspace = r'\\Dataserver0\gpw\GPW4\Preprocessing\Country'
arcpy.env.workspace = workspace
scratch = arcpy.env.scratchFolder

# check if directory already exists, if it does exit
newDir = workspace + os.sep + iso
if arcpy.Exists(newDir):
    sys.exit("Directory already exists")
else:
    # create preprocessing iso directory
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
    # create personal geodatabases
    arcpy.CreatePersonalGDB_management(ingestCensus,iso + "_ingest")
    arcpy.CreatePersonalGDB_management(match,iso + "_match_access")
    print "Created file GDBs"
    arcpy.AddMessage("Created file GDBs")

    # create growth rate folder
    growthRate = r'\\Dataserver0\gpw\GPW4\GrowthRate'
    growthRateFolder = growthRate + os.sep + iso
    arcpy.CreateFolder_management(growthRate, iso)
    print "Created growth rate folder"
    arcpy.AddMessage("Created growth rate folder")
                     
    # create growth rate personal geodatabase
    arcpy.CreatePersonalGDB_management(growthRateFolder,iso + "_growth_rate")
    print "Created growth rate personal GDB"
    arcpy.AddMessage("Created growth rate personal GDB")
    
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

    # Add UBID field to gadm2_adminX
    suffixInt = int(suffix)
    gadm2AdminX = gadm2GDB + os.sep + iso + "_admin" + suffix
    arcpy.AddField_management(gadm2AdminX,"UBID","TEXT","","",50)

    if suffixInt == 0:
        calculationExpression = '[ID_0]'
    elif suffixInt == 1:
        calculationExpression = '[ID_0] & "_" & [ID_1]'
    elif suffixInt == 2:
        calculationExpression = '[ID_0] & "_" & [ID_1] & "_" & [ID_2]'
    elif suffixInt == 3:
        calculationExpression = '[ID_0] & "_" & [ID_1] & "_" & [ID_2] & "_" & [ID_3]'
    elif suffixInt == 4:
        calculationExpression = '[ID_0] & "_" & [ID_1] & "_" & [ID_2] & "_" & [ID_3] & "_" & [ID_4]'
    elif suffixInt == 5:
        calculationExpression = '[ID_0] & "_" & [ID_1] & "_" & [ID_2] & "_" & [ID_3] & "_" & [ID_4] & "_" & [ID_5]'
    else:
        print "You have more than 5 admin levels in GADM.  You need to add the UBID manually."
        arcpy.AddMessage("You have more than 5 admin levels in GADM.  You need to add the UBID manually.")
        calculationExpression = "<NULL>"
    arcpy.CalculateField_management(gadm2AdminX,"UBID",calculationExpression)
    print "UBID added to GADMv2"
    arcpy.AddMessage("UBID added to GADMv2")
   
    # Copy gdb
    arcpy.Copy_management(gadm2GDB,ingestBoundary + os.sep + "gadm2.gdb")

print "done"
arcpy.AddMessage("done")   
print datetime.datetime.now() - startTime  
