# Kytt MacManus
# 7-25-14
# merge_rasters.py
# script to merge country rasters into global raster

# import libraries
import os, arcpy, datetime

# set counter
startTime = datetime.datetime.now()

# Check out Spatial Analyst
arcpy.CheckOutExtension("SPATIAL")

# Define variables
workspace = r'\\Dataserver0\gpw\GPW4\Gridding\country\rasters'
outGDB = r'\\Dataserver0\gpw\GPW4\Gridding\global\inputs\rasters\CONSTANT_BOUND_BOXES.gdb'

# Set Environments
arcpy.env.workspace = workspace

# List GDB
gdbs = arcpy.ListWorkspaces("*_grids.gdb")

for gdb in gdbs:
    iso = os.path.basename(gdb)[:3]
    templateFile = gdb + os.sep + iso.upper() + "_AREA"
    if not arcpy.Exists(templateFile):
        print iso
    else:
        outputFile = outGDB + os.sep + iso.upper() + "_CONSTANT"
        if not arcpy.Exists(outputFile):
            try:
                arcpy.env.extent = templateFile
                arcpy.env.cellSize = templateFile
                outConst = arcpy.sa.CreateConstantRaster(1,"INTEGER")
                outConst.save(outputFile)
                print "Created " + outputFile
                del outConst
            except:
                print arcpy.GetMessages()
        



print datetime.datetime.now()-startTime
arcpy.AddMessage(datetime.datetime.now()-startTime)
 
