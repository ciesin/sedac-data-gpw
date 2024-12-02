# check proportions
import arcpy
import os

ws = r'\\Dataserver0\gpw\GPW4\Gridding\country\rasters'
arcpy.env.workspace = ws
gdbs = arcpy.ListWorkspaces("*","FILEGDB")
for gdb in gdbs:
    arcpy.env.workspace = gdb 
    rasters = arcpy.ListRasters("*")
    for raster in rasters:
        minimum = str(arcpy.GetRasterProperties_management(raster,"MINIMUM")[0])
        if minimum == "0":
            pass
        else:
            print raster
            print minimum + " is the min value"
