# attribute_compilation.py
# compile raster attributes based on pointid

import arcpy

##startTime = datetime.datetime.now()

# define workspace
workspace = r"\\Dataserver0\gpw\scratch\final\unmasked"
arcpy.env.workspace = workspace
# list rasters
rasters = arcpy.ListRasters("*")
import numpy
for raster in rasters:
##    outRaster = workspace.replace("unmasked","masked") + raster
##    npArray = arcpy.RasterToNumPyArray(raster)
##    numpy.putmask(npArray,npArray==npArray[0][0],-1)
##    result = arcpy.NumPyArrayToRaster(npArray)
##    result.save(outRaster)
    print "Created " + outRaster




