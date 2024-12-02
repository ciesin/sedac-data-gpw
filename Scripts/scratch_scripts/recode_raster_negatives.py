# recode_negatives.py
# the initial gridding algorithm had a slight error which lead to some
# pop count calculations being Negative. this script postprocesses the
# countries which were affected to correct for this.  the gridding algorithm
# has been updated such that this should not be a continued problem
# Kytt MacManus
# September 27, 2013

# import libraries
import arcpy, os, sys
import datetime

root =r'\\Dataserver0\gpw\GPW4\Gridding\country\rasters'

# Set workspace
arcpy.env.workspace = root

# Check out SA extension
arcpy.CheckOutExtension("SPATIAL")

# List file GDBS
gdbs = arcpy.ListWorkspaces("*old.gdb","FILEGDB")
#iterate
for gdb in gdbs:
    # parse iso code
    iso = os.path.basename(gdb)[:3]
    # Create Output Folder
    outputRoot = r'\\Dataserver0\gpw\GPW4\Gridding\country\rasters'
    outGDB = iso + "_grids"
    outputFolder = outputRoot + os.path.sep + outGDB + ".gdb"
    if not arcpy.Exists(outputFolder):
        arcpy.CreateFileGDB_management(outputRoot,outGDB)
        print "Created " + outputFolder
        arcpy.AddMessage("Created " + outputFolder)
    else:
        arcpy.AddMessage(outputFolder + " already exists")
    # set workspace to gdb
    arcpy.env.workspace = gdb
    # List Rasters
    rasters = arcpy.ListRasters("*AREA*")
    for raster in rasters:
        time = datetime.datetime.now()
        print "Processing " + raster
        outRaster = outputFolder + os.sep + raster
        try:
            outSetNull = arcpy.sa.SetNull(raster, raster, "VALUE < 0")
            outSetNull.save(outRaster)
            print "Created " + outRaster
            print str(datetime.datetime.now() - time)
        except:
            print arcpy.GetMessages
