# Kytt MacManus
# July 24 2014
# Copy Grids to 

# Import Libraries
import arcpy, os, csv
import datetime
startTime = datetime.datetime.now()
# Define Workspace Variable
workspace = r'\\Dataserver0\gpw\GPW4\Gridding\country\inputs'
outGDB = r'\\Dataserver0\gpw\GPW4\Gridding\global\inputs\un_adjustment_tables.gdb'
# Assign workspace environment for ArcPy
arcpy.env.workspace = workspace
# List GDBs in workspace environment
gdbs = arcpy.ListWorkspaces("*","FILEGDB")
gdbs.sort()
# Define ListTables Wildcard
wildCard = "_un_adjustment"
 #iterate
for gdb in gdbs:
    # Parse COUNTRYCODE
    COUNTRYCODE = os.path.basename(gdb)[:-4]
    # Parse input Raster
    inTable = gdb + os.sep + COUNTRYCODE + wildCard
    # Parse output Raster
    outTable = outGDB + os.sep + COUNTRYCODE + wildCard

    # Copy Raster
    if not arcpy.Exists(outTable):
        try:
            arcpy.CopyRows_management(inTable,outTable)
            print "Created " + outTable
            arcpy.AddMessage("Created " + outTable)
        except:
            print arcpy.GetMessages()
            arcpy.AddMessage(arcpy.GetMessages())
    else:
        print outTable + " already exists"
   
                          
print datetime.datetime.now() - startTime
arcpy.AddMessage(datetime.datetime.now() - startTime)
