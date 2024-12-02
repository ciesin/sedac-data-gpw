import os
import multiprocessing
import arcpy
from arcpy import env
import datetime

# set counter
startTime = datetime.datetime.now()

# define workspace
workspace = r'\\Dataserver0\gpw\GPW4\Gridding\country\inputs\usa_state\rasters'
# Set Environments
arcpy.env.workspace = workspace
# Check out Spatial Analyst
arcpy.CheckOutExtension("SPATIAL")
gdbs = arcpy.ListWorkspaces("*", "FileGDB")
rasterWS = workspace + os.sep + 'usa_akeast_grids.gdb'
arcpy.env.workspace = rasterWS
# List Rasters
rasters = arcpy.ListRasters("*input*")
for raster in rasters:
    print raster
    arcpy.env.cellSize = raster
    rasterParse = raster.split("_")
    name = rasterParse[0]
    suffix = "" 
    x = len(rasterParse[2:])
    i = 2
    while x:
        suffix = suffix + "_" + rasterParse[i]
        i = i + 1
        x = x - 1
    print suffix
    
    rastList = str(raster)
    cellList = [rasterWS + os.sep + raster]
    j = 0
    for gdb in gdbs:
        if j == 0:
            j = j + 1
            pass
        else:
            appendRaster = gdb + os.sep + os.path.basename(gdb)[:-10].upper() + suffix
            rastList = rastList + ";" +  appendRaster
            cellList.append(appendRaster)
    # First calculate the extent
    outExtent = r'\\dataserver0\gpw\GPW4\Gridding\country\inputs\usa_state\usa_extent\us_extent.tif'
    if not arcpy.Exists(outExtent):
        try:
            print "Mosaic Processing"
##            arcpy.MosaicToNewRaster_management(rastList,
##                                               r'E:\gpw4\can\final\CAN.gdb',
##                                               "CAN_EXTENT",
##                                               arcpy.SpatialReference(4326),
##                                               "8_BIT_UNSIGNED",
##                                               arcpy.env.cellSize,
##                                               "1", "FIRST","FIRST")
        except:
            print arcpy.GetMessages()
    # Set Extent Environment
    arcpy.env.extent = outExtent
    # Calculate Cell Statistics
    outCellStats = r'\\dataserver0\gpw\GPW4\Gridding\country\inputs\usa_state\usa_grids.gdb' + os.sep + name + suffix
    if not arcpy.Exists(outCellStats):
        print "Cell Stats Processing"
        try:
            cellStats = arcpy.sa.CellStatistics(cellList, "SUM", "DATA")
            cellStats.save(outCellStats)
            del cellStats
            print "Created " + outCellStats
        except:
            print arcpy.GetMessages()

print(datetime.datetime.now()-startTime)
 
