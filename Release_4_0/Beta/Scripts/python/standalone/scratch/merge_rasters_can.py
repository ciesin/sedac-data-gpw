# Kytt MacManus
# 9-14-15
# merge_rasters.py

# import libraries
import os, arcpy, datetime
# set counter
startTime = datetime.datetime.now()
# Check out Spatial Analyst
arcpy.CheckOutExtension("SPATIAL")
# define output gdb, create if it doesn't exist
outGDB = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\rasters\can\can.gdb'
iso = "CAN"
if not arcpy.Exists(outGDB):
    arcpy.CreateFileGDB_management(os.path.dirname(outGDB),os.path.basename(outGDB)[:-4])
# define outExtent
outExtent = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\global\ancillary\gpw4_extent.tif'
arcpy.env.extent = outExtent
# set workspace
ws = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\rasters\can\tiles'
arcpy.env.workspace = ws
# list gdbs
gdbs = arcpy.ListWorkspaces("*","FILEGDB")
# list variables to grid
#"AREAKMMASKED","WATERAREAKM",
varIDS = ["AREAKMMASKED","WATERAREAKM","E_ATOTPOPBT_1975_CNTM",
          "E_ATOTPOPBT_1990_CNTM","E_ATOTPOPBT_2000_CNTM",
          "E_ATOTPOPBT_2005_CNTM","E_ATOTPOPBT_2010_CNTM",
          "E_ATOTPOPBT_2015_CNTM","E_ATOTPOPBT_2020_CNTM",
          "E_ATOTPOPFT_2010_CNTM","E_ATOTPOPMT_2010_CNTM"]
for varID in varIDS:
    gridRasters = [os.path.join(gdb, os.path.basename(gdb)[:-4].upper() + "_" + varID) for gdb in gdbs]
    outRaster = outGDB + os.sep + iso + "_" + varID
    if not arcpy.Exists(outRaster):
        print "Cell Stats Processing for " +  iso + "_" + varID
        try:
            cellStats = arcpy.sa.CellStatistics(gridRasters, "SUM", "DATA")
            cellStats.save(outRaster)
            del cellStats
            arcpy.BuildPyramidsandStatistics_management(outRaster)
            print "Created " + outRaster
        except:
            print arcpy.GetMessages()
print datetime.datetime.now()-startTime
