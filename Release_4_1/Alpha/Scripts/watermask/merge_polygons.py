import arcpy, os
from arcpy import env

polygdb = r'F:\GPW\watermask\tiled_rasters\polygon_tiles.gdb'
outfc = r'F:\GPW\watermask\merged_water_polygon.gdb\ESA_global_water'

env.workspace = polygdb

fcList = arcpy.ListFeatureClasses()

for fc in fcList:
    arcpy.Append_management(fc,outfc,"NO_TEST")
    print fc

