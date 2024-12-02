# Kytt MacManus
# January 5, 2014

# Import Libraries
import arcpy, os, csv
import multiprocessing
import datetime

# set counter
startTime = datetime.datetime.now()
# Define Workspace Variable
workspace = r'E:\gpw\california\sandiego\tracts'

# Assign workspace environment for ArcPy
arcpy.env.workspace = workspace
arcpy.env.overwriteOutput = True

# List GDBs in workspace environment
gdbs = arcpy.ListWorkspaces("*","FILEGDB")
gdbs.sort()
for gdb in gdbs:
    #print gdb
    # define fishnet
    fishnet = gdb + os.sep + os.path.basename(gdb)[:-4] + "_fishnet"
    gridGDB = r'E:\gpw\california\sandiego\rasters' + os.sep + os.path.basename(gdb)[:-4] + "_grids.gdb"
    # grab TRACTCODE
    TRACTCODE = os.path.basename(gdb)[:-4]
    lyr = TRACTCODE + "_lyr"
    arcpy.MakeFeatureLayer_management(fishnet,lyr,'"' + "SINGLEZONE" + '"' + "IS NULL")
    count = arcpy.GetCount_management(lyr)
    if count[0] == "0":
        arcpy.Delete_management(lyr)
    else:
        print count[0]
        print fishnet
    
        # add field for single zone
        try:
            arcpy.AddField_management(fishnet,"SINGLEZONE","SHORT")
        except:
            print arcpy.GetMessages()
        # calculate SINGLEZONE
        try:
            arcpy.CalculateField_management(fishnet,"SINGLEZONE",1)
            print "Calculated SINGLEZONE"
        except:
            print arcpy.GetMessages()
        # Coordinate System
        wgs84 = arcpy.SpatialReference(4326)
        # Describe Fish
        desc = arcpy.Describe(fishnet)
        # Calculate Raster Extent
        extent = desc.Extent
        xmin = int(round(extent.XMin - .5))
        xmax = int(round(extent.XMax + .5))
        ymin = int(round(extent.YMin - .5))
        ymax = int(round(extent.YMax + .5))
        # Lines per degree, determines the output resolution 120 = 30 arc-seconds resolution
        # 1 degree divided into 120 parts is 30 seconds
        linespd = 3600## Update As Needed
        cellSize = 1.0 / linespd
        # define environments
        arcpy.env.extent = arcpy.Extent(xmin,ymin,xmax,ymax)
        arcpy.env.outputCoordinateSystem = wgs84
        arcpy.env.cellSize = cellSize
        # grid SINGLEZONE
        outGrid = gridGDB + os.sep + os.path.basename(gdb)[:-4]
        try:
            arcpy.PolygonToRaster_conversion(fishnet,"SINGLEZONE",outGrid,'CELL_CENTER','#',cellSize)
            print "gridded"
        except:
            print arcpy.GetMessages()


     

print datetime.datetime.now() - startTime

