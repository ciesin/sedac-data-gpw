import os
import multiprocessing
import arcpy
from arcpy import env
import datetime

# set counter
startTime = datetime.datetime.now()

# define workspace
workspace = r'\\Dataserver0\gpw\GPW4\Gridding\country\inputs\bra_state\preprocess'
iso = "BRA"
outWS = r'\\Dataserver0\gpw\GPW4\Gridding\country\inputs\bra_state\extent\brazil.gdb'
# Set Environments
arcpy.env.workspace = workspace
# Check out Spatial Analyst
arcpy.CheckOutExtension("SPATIAL")
# List File GDBs
gdbs = arcpy.ListWorkspaces("*", "FileGDB")
# Assign Raster WS
rasterWS = gdbs[0]
arcpy.env.workspace = rasterWS
# List Rasters
rasters = arcpy.ListRasters("*_atotpop*")
for raster in rasters:
    print raster
    arcpy.env.cellSize = raster
    rasterParse = raster.split("_")
    name = raster.replace(rasterParse[0],iso)
    if len(rasterParse) == 2:
        suffix = "_AREAPOPPRODUCT"
    else:
        suffix = "_" + rasterParse[1] + "_" + rasterParse[2] #+ "_" + rasterParse[3] + "_" + rasterParse[4]
    outCellStats = outWS + os.sep + name
    rastList = str(gdbs[0] + os.sep + raster)
    cellList = [gdbs[0] + os.sep + raster]
    i = 0
    for gdb in gdbs:
        if i == 0:
            i = i + 1
            pass
        else:
            appendRaster = gdb + os.sep + os.path.basename(gdb)[:-4] + suffix
            rastList = rastList + ";" +  appendRaster
            cellList.append(appendRaster)

    # THIS SECTION NEEDS WORK!!
    # First calculate the extent
    outExtent = r'\\Dataserver0\gpw\GPW4\Gridding\country\inputs\bra_state\extent\brazil.gdb\BRA_EXTENT'
    if not arcpy.Exists(outExtent):
        try:
            print "Mosiac Processing"
            arcpy.MosaicToNewRaster_management(rastList,
                                               r'\\Dataserver0\gpw\GPW4\Gridding\country\inputs\bra_state\extent\brazil.gdb',
                                               "BRA_EXTENT",
                                               arcpy.SpatialReference(4326),
                                               "8_BIT_UNSIGNED",
                                               arcpy.env.cellSize,
                                               "1", "FIRST","FIRST")
        except:
            print arcpy.GetMessages()
    # Set Extent Environment
    arcpy.env.extent = outExtent
    # Calculate Cell Statistics
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
 
