# Kytt MacManus
# July 24 2014
# Copy Grids to 

# Import Libraries
import arcpy, os, csv
import datetime
startTime = datetime.datetime.now()
# Define Workspace Variable
workspace = r'\\Dataserver0\gpw\GPW4\Gridding\country\inputs'
outGDB = r'\\Dataserver0\gpw\GPW4\Gridding\global\inputs\agr_tables.gdb'
# Assign workspace environment for ArcPy
arcpy.env.workspace = workspace
# List GDBs in workspace environment
gdbs = arcpy.ListWorkspaces("*","FILEGDB")
gdbs.sort()

#iterate
for gdb in gdbs:
    arcpy.env.workspace = gdb
    # Parse COUNTRYCODE
    COUNTRYCODE = os.path.basename(gdb)[:-4]
    tables = arcpy.ListTables("*growth*")
    for table in tables:
        # Parse output Raster
        outTable = outGDB + os.sep + COUNTRYCODE + "_growth_rate"

        # Copy Raster
        if not arcpy.Exists(outTable):
            try:
                copyTime = datetime.datetime.now()
                arcpy.CopyRows_management(table,outTable)
                print "Created " + outTable
                print datetime.datetime.now() - copyTime
                arcpy.AddMessage("Created " + outTable)
            except:
                print arcpy.GetMessages()
                arcpy.AddMessage(arcpy.GetMessages())
        else:
            print outTable + " already exists"
       
                          
print datetime.datetime.now() - startTime
arcpy.AddMessage(datetime.datetime.now() - startTime)
