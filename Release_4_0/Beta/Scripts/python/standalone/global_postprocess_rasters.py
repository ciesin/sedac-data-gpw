import arcpy, os, datetime
from arcpy.sa import *
arcpy.CheckOutExtension('SPATIAL')

arcpy.env.workspace = r'F:\gpw\global\gpw-4-global-rasters.gdb'
outGDB = r'F:\gpw\global\gpw4.gdb'

##NOTE- PRODUCED ANCILLARY MASKS MANUALLY
waterMask = r'F:\gpw\global\ancillary.gdb\GL_WATERMASK_TOTALWATER_ISNULL'
nullMask = r'F:\gpw\global\ancillary.gdb\GL_MEAN_ADMIN_UNIT_AREA_ISNULL'#r'F:\gpw\global\ancillary.gdb\GL_ISNULL'
areaMask = r'F:\gpw\global\gpw-4-global-rasters.gdb\GL_AREAKMMASKED'
rasters = arcpy.ListRasters("*WATERAREA*")
for raster in rasters:
    print "Processing " + raster
    outRaster = outGDB + os.sep + raster
    if not arcpy.Exists(outRaster):
        procTime = datetime.datetime.now()
        # do first step in memory
        arcpy.env.mask = areaMask
        rasterWithZeros = Con(Raster(nullMask)==1,0,Raster(raster))
        print "completed first conditional"
        # complete setnull
        finalRaster = SetNull(Raster(waterMask)==0,rasterWithZeros)
        print "completed second conditional"
        finalRaster.save(outRaster)
        arcpy.BuildPyramidsandStatistics_management(outRaster)
        print "saved final raster. process time: " + str(datetime.datetime.now()-procTime)
