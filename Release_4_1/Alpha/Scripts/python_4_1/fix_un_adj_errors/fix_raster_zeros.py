# Kytt MacManus
# Jane Mills
# 12-4-17
# merge_rasters.py

import arcpy, os, datetime, multiprocessing, socket
arcpy.CheckOutExtension("SPATIAL")
from arcpy.sa import *
arcpy.env.overwriteOutput = True

print "Processing"

inWS = r'D:\gpw\release_4_1\global_tifs\processing'
arcpy.env.workspace = inWS
rasterList = [os.path.join(inWS,r) for r in arcpy.ListRasters("*setnull*")]

for inRaster in rasterList:
    year = os.path.basename(inRaster)[8:12]
    print year
    outFolder = r'D:\gpw\release_4_1\global_tifs'
    outRaster2 = os.path.join(outFolder,'processing','gpw_une_'+year+'_times.tif')
    copyRaster = os.path.join(outFolder,'gpw_v4_une_atotpopbt_'+year+'_cntm_30_sec.tif')

    popcells = r'D:\gpw\release_4_1\global_tifs\processing\scratch\gpw_pop_cells.tif'
    outExtent = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\ancillary\extents\gpw4_extent_30_sec.tif'
    arcpy.env.extent = outExtent
    arcpy.env.compression = "LZW"
    arcpy.env.mask = inRaster

    arcpy.gp.Times_sa(inRaster,popcells,outRaster2)
    arcpy.CopyRaster_management(outRaster2,copyRaster)
    arcpy.BuildPyramidsandStatistics_management(copyRaster)
    print "Processed "+ inRaster

