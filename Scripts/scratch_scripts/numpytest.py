import arcpy,os
# define workspace
workspace = r"\\Dataserver0\gpw\scratch\final\unmasked"
arcpy.env.workspace = workspace
# list rasters
rasters = arcpy.ListRasters("*")
import numpy
for raster in rasters:
    arcpy.env.cellSize = 0.00027777778
    arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(4326)
    outRaster = workspace.replace("unmasked","masked_v2") + os.sep + raster
    npArray = arcpy.RasterToNumPyArray(raster)
    numpy.putmask(npArray,npArray==npArray[0][0],-1)
    result = arcpy.NumPyArrayToRaster(npArray)
    result.save(outRaster)
    print "Created " + outRaster
