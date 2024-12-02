# Kytt MacManus
# January 5, 2014

# Import Libraries
import arcpy, os, csv, datetime
arcpy.CheckOutExtension("SPATIAL")
# Define Workspace Variable
workspace = r'\\Dataserver0\gpw\GPW4\Gridding\country\rasters\scratch\values_less_than_zero'
outWorkspace = r'\\Dataserver0\gpw\GPW4\Gridding\country\rasters'

###TEMP
extent = workspace + os.sep + "can_grids.gdb" + os.sep + "CAN_EXTENT"
# Assign workspace environment for ArcPy
arcpy.env.workspace = workspace
arcpy.CheckOutExtension("SPATIAL")
# List GDBs in workspace environment
gdbs = arcpy.ListWorkspaces("can*","FILEGDB")
gdbs.sort()
# iterate
for gdb in gdbs:
    ISO = os.path.basename(gdb)[:3]
    arcpy.env.workspace = gdb
    # Create Output Folder
    outputRoot = r'\\Dataserver0\gpw\GPW4\Gridding\country\rasters'
    outGDB = ISO.lower() + "_grids"
    outputFolder = outputRoot + os.path.sep + outGDB + ".gdb"
    if not arcpy.Exists(outputFolder):
        arcpy.CreateFileGDB_management(outputRoot,outGDB)
        print "Created " + outputFolder
        arcpy.AddMessage("Created " + outputFolder)
    else:
        arcpy.AddMessage(outputFolder + " already exists")
    outGDB = outputFolder 

    ####RECODE RASTER METHOD####
    # list rasters
    rasters = arcpy.ListRasters("*AREA")
    for raster in rasters:
        outRaster = outGDB + os.sep + raster
        if not arcpy.Exists(outRaster):
            conTime = datetime.datetime.now()
            # recode by condition
            arcpy.env.extent = extent
            # Set local variables
            inRaster = arcpy.sa.Raster(raster)
            inTrueConstant = 0
            inFalseRaster = arcpy.sa.Raster(raster)
            whereClause = """"VALUE" <= 0"""
            arcpy.gp.Con_sa(raster,"0",outRaster,raster,""""VALUE" <= 0""")
##            # Execute Con
##            outCon = arcpy.sa.Con(inRaster, inTrueConstant, inFalseRaster, whereClause)
##            # Save the outputs 
##            outCon.save(outRaster)
            print "Created " + outRaster
            print str(datetime.datetime.now()-conTime)
