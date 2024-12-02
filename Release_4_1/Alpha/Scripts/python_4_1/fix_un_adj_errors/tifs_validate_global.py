#Jane Mills
#3/9/17
#summarize rasters and compare to tables

import arcpy, os, csv,sys
from arcpy import env
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")

arcpy.env.overwriteOutput = True

root = r'D:\gpw\release_4_1\global_tifs'
outGDB = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\validation\scratch.gdb'
extent = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\ancillary\gpw4_extent.tif'

env.workspace = root
rasterList = arcpy.ListRasters()
#rasterList = arcpy.ListRasters("*une_*cntm*30_sec*")
rasterList.sort()

for r in rasterList:
    print r
    outTable = os.path.join(outGDB,'temp')
    arcpy.gp.ZonalStatisticsAsTable_sa(extent,"Value",r,outTable,"DATA","SUM")
    rsum = 0
    with arcpy.da.SearchCursor(outTable,'SUM') as cursor:
        for row in cursor:
            rsum += row[0]
    print rsum

print "done"

