# Kytt MacManus
# 9-14-15
# merge_rasters.py

# import libraries
import os, arcpy, datetime
# set counter
startTime = datetime.datetime.now()
# Check out Spatial Analyst
arcpy.CheckOutExtension("SPATIAL")
isos = ["GL"]
for iso in isos:
    print iso
    # define output gdb, create if it doesn't exist
    outGDB = r'H:\gpw\rasters\merge' + os.sep + iso.lower() + '.gdb'
    if not arcpy.Exists(outGDB):
        arcpy.CreateFileGDB_management(os.path.dirname(outGDB),iso.lower())
    # define outExtent
    outExtent = r'\\Dataserver0\gpw\GPW4\Release_4_0\Prod\Gridding\global\ancillary\gpw4_extent.tif'
    arcpy.env.extent = outExtent
    # set workspace
    ws = r'H:\gpw\rasters\fgdb'
    arcpy.env.workspace = ws
    # list gdbs
    gdbs = arcpy.ListWorkspaces("*","FILEGDB")
    print len(gdbs)
    for gdb in gdbs:
        arcpy.env.workspace = gdb
        # define root name
        rootName = os.path.basename(gdb)[:-4]
        # list variables to grid
        varIDS = arcpy.ListRasters("*WOMCHILD*")
        # post process to remove the rootname
        varIDS = [variable[len(rootName):] for variable in varIDS]
        break
    meanArea = "_MEAN_ADMINAREAKMMASKED"
    for varID in varIDS:
        print varID
        procTime = datetime.datetime.now()
        gridRasters = [os.path.join(gdb, os.path.basename(gdb)[:-4].upper() + varID) for gdb in gdbs]
        outRaster = outGDB + os.sep + iso + varID    
        if not arcpy.Exists(outRaster):
            print "Cell Stats Processing: " + str(len(gridRasters)) + " files"
            try:
                if varID == meanArea:
                    cellStats = arcpy.sa.CellStatistics(gridRasters, "MEAN", "DATA")
                else:
                    cellStats = arcpy.sa.CellStatistics(gridRasters, "SUM", "DATA")
                print "Created " + outRaster
                cellStats.save(outRaster)
                print "Saved to disk"
                del cellStats
                arcpy.BuildPyramidsandStatistics_management(outRaster)
                print "Built pyramids"
                print datetime.datetime.now()-procTime
            except:
                print arcpy.GetMessages()
print datetime.datetime.now()-startTime
