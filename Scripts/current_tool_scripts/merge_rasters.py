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

ws = r'\\Dataserver0\gpw\GPW4\Gridding\global\inputs\rasters_v4.0_alpha2'
arcpy.env.workspace = ws

gdbs = arcpy.ListWorkspaces("*mean_admin*","FILEGDB")
                    
for gdb in gdbs:
    print gdb
    # define workspace #PARAMETER
    workspace = gdb

    # define output file
    outCellStatsGrid = r'\\Dataserver0\gpw\GPW4\Gridding\global\inputs\rasters_v4.0_alpha2\merged\global_grids.gdb' + os.sep + "GL_" + os.path.basename(workspace)[:-4]

    # define outExtent
    outExtent = r'\\Dataserver0\gpw\GPW4\Gridding\global\ancillary\gpw4_extent.tif'
    # define water mask
    waterMask = r'\\Dataserver0\gpw\GPW4\Gridding\global\ancillary\gpw4_water_mask.tif'
    # Set Environments
    arcpy.env.workspace = workspace

    # List Rasters
    cellList = arcpy.ListRasters("*")

    arcpy.env.extent = outExtent

    # Calculate Cell Statistics
    if not arcpy.Exists(outCellStatsGrid):
        print "Cell Stats Processing"
        arcpy.AddMessage("Cell Stats Processing")
        try:
            cellStats = arcpy.sa.CellStatistics(cellList, "SUM", "DATA")#arcpy.sa.SetNull(arcpy.sa.IsNull(waterMask)==0,arcpy.sa.CellStatistics(cellList, "SUM", "DATA"))
            cellStats.save(outCellStatsGrid)
            del cellStats
            print "Created " + outCellStatsGrid
            arcpy.AddMessage("Created " + outCellStatsGrid)
        except:
            print arcpy.GetMessages()
            arcpy.AddMessage(arcpy.GetMessages())
    else:
        print outCellStatsGrid + " already exists"
        arcpy.AddMessage(outCellStatsGrid + " already exists")
    print datetime.datetime.now()-startTime
    arcpy.AddMessage(datetime.datetime.now()-startTime)
     
