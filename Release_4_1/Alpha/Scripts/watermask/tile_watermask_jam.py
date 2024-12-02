import arcpy, os
from arcpy import env
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")

ingdb = r'F:\GPW\watermask\tiled_rasters\tiles.gdb'
outgdb = r'F:\GPW\watermask\tiled_rasters\raster_tiles.gdb'
polygdb = r'F:\GPW\watermask\tiled_rasters\polygon_tiles.gdb'
inRaster = r'F:\GPW\watermask\ESAWater\ESACCI-LC-L4-WB-Map-150m-P13Y-2000-v4.0.tif'

env.workspace = ingdb

fcList = arcpy.ListFeatureClasses()

for fc in fcList[99:]:
    #extract raster
    outRaster = os.path.join(outgdb,"raster_"+fc[5:])
    outExtractByMask = ExtractByMask(inRaster,fc)

    #reclassify the land to null, water to 1
    remap = RemapValue([[2,1]])
    outReclassify = Reclassify(outExtractByMask,"Value",remap,"NODATA")
    outReclassify.save(outRaster)

    #need to check if reclassified raster is empty
    result = arcpy.GetCount_management(outRaster)
    count = int(result.getOutput(0))
    if count == 1:
        outPoly = os.path.join(polygdb,"polygon_"+fc[5:])
        arcpy.RasterToPolygon_conversion(outRaster,outPoly,"NO_SIMPLIFY")
        print "converted " + fc
    elif count == 0:
        print fc+" is empty"
    else:
        print "reclassify didn't work for "+fc

