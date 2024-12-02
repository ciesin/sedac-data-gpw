import arcpy, os, datetime
from arcpy.sa import *
arcpy.CheckOutExtension('SPATIAL')

arcpy.env.workspace = r'D:\gpw\rasters\merge\gl.gdb'
outGDB = r'D:\gpw\rasters\merge\gl_post_process.gdb'

##NOTE- PRODUCED ANCILLARY MASKS MANUALLY
waterMask = r'D:\gpw\rasters\merge\gl_rasters.gdb\GL_WATERMASK_TOTALWATER_ISNULL'
mask = r'D:\gpw\rasters\merge\gl_rasters.gdb\GL_MASK'
rasters = arcpy.ListRasters("*")
for raster in rasters:
    print "Processing " + raster
    outRaster = outGDB + os.sep + raster
    if not arcpy.Exists(outRaster):
        procTime = datetime.datetime.now()
        arcpy.env.mask = mask
        # complete setnull
        finalRaster = SetNull(Raster(waterMask)==0,Raster(raster))
        print "completed conditional"
        finalRaster.save(outRaster)
        arcpy.BuildPyramidsandStatistics_management(outRaster)
        print "saved final raster. process time: " + str(datetime.datetime.now()-procTime)
