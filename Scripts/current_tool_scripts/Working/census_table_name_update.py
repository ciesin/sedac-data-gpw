# Kytt MacManus
# July 8, 2014

# Import Libraries
import arcpy, os, csv
import datetime
startTime = datetime.datetime.now()
# Define Workspace Variable
workspace = r'\\Dataserver0\gpw\GPW4\Gridding\country\inputs'
outGDB = r'\\Dataserver0\gpw\GPW4\Gridding\global\input_population_tables.gdb'
lookup = r'\\Dataserver0\gpw\GPW4\Gridding\validation\ancillary.gdb\census_table_names'
# Assign workspace environment for ArcPy
arcpy.env.workspace = workspace

# List GDBs in workspace environment
gdbs = arcpy.ListWorkspaces("*","FILEGDB")
gdbs.sort()

# iterate
for gdb in gdbs:
    arcpy.env.workspace = gdb
    COUNTRYCODE = os.path.basename(gdb)[:-4]
    # Create Search Cursor
    rows = arcpy.SearchCursor(lookup,"COUNTRYCODE" + "=" + "'"+COUNTRYCODE+"'")
    for row in rows:
        CENSUSTABLE = gdb + os.sep + str(row.CENSUSTABLE)
        CENSUSTABLENAME = str(row.CENSUSTABLE)
        MISSINGADMININFO = str(row.MISSINGADMININFO)
        MISSINGYEARINFO = str(row.MISSINGYEARINFO)
        NEWNAME = COUNTRYCODE.lower() + "_" + MISSINGADMININFO + "_" + MISSINGYEARINFO + "_input_population"
        renameFile = gdb + os.sep + NEWNAME
        copyFile = outGDB + os.sep + NEWNAME
        # Test for lock
        if arcpy.Exists(CENSUSTABLE):
            if arcpy.TestSchemaLock(CENSUSTABLE)==False:
                print "Lock on " + CENSUSTABLE
            else:
                # Rename
                if not arcpy.Exists(renameFile):
                    try:
                        arcpy.Rename_management(CENSUSTABLE,renameFile)
                        print "Created " + renameFile
                    except:
                        print arcpy.GetMessages()
                # Copy
                if not arcpy.Exists(copyFile):
                    try:
                        arcpy.CopyRows_management(renameFile,copyFile)
                        print "Created " + copyFile
                    except:
                        print arcpy.GetMessages()
                          
print datetime.datetime.now() - startTime
