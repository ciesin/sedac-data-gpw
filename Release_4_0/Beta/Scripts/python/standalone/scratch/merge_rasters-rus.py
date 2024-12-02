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
outGDB = r'Z:\GPW4\Beta\Gridding\rasters\rus\rus.gdb'
iso = "RUS"
if not arcpy.Exists(outGDB):
    arcpy.CreateFileGDB_management(os.path.dirname(outGDB),os.path.basename(outGDB)[:-4])
# define outExtent
outExtent = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\global\ancillary\gpw4_extent.tif'
arcpy.env.extent = outExtent
# set workspace
ws = r'Z:\GPW4\Beta\Gridding\rasters\rus\tiles'
arcpy.env.workspace = ws
# list gdbs
gdbs = arcpy.ListWorkspaces("*","FILEGDB")
# list variables to grid
#"AREAKMMASKED","WATERAREAKM",
varIDS = ["AREAKMMASKED"]
for varID in varIDS:
    gridRasters = [os.path.join(gdb, os.path.basename(gdb)[:-4].upper() + "_" + varID) for gdb in gdbs]
    outRaster = outGDB + os.sep + iso + "_" + varID
    if not arcpy.Exists(outRaster):
        print "Cell Stats Processing: " + str(len(gridRasters)) + " files"
        try:
            cellStats = arcpy.sa.CellStatistics(gridRasters, "SUM", "DATA")
            print "Created " + outRaster
            cellStats.save(outRaster)
            print "Saved to disk"
            del cellStats
            arcpy.BuildPyramidsandStatistics_management(outRaster)
            print "Built pyramids"
        except:
            print arcpy.GetMessages()
print datetime.datetime.now()-startTime
