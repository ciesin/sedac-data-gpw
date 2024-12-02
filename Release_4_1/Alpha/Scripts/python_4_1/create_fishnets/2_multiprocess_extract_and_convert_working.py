# multiprocess_extract_and_convert
# extract pointids to country mask 
## NOTE THIS CODE WAS RUN ON DEVSEDARC VM PREVIOUSLY
## PATH MAY NEED TO BE UPDATED

import os
import re
import arcpy
from datetime import datetime
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")

def update_rasters(raster):
    outRaster = r"F:\GPW\fishnets\output_tifs_ids" + os.sep + os.path.basename(raster.lower())[:-4] + "_ids"
    if arcpy.Exists(outRaster):
        print outRaster + " already exists"
    else:
        scratchDir = r"F:\GPW\fishnets\scratch" + os.sep + os.path.basename(raster.lower())[:-4]
        if not arcpy.Exists(scratchDir):
            os.mkdir(scratchDir)
        arcpy.env.scratchWorkspace = scratchDir         
        pointid = r"F:\GPW\fishnets\gpw4_30second_ids.tif" # it is important to extract from this layer
         
        WGS84 = arcpy.SpatialReference(4326)
        arcpy.env.outputCoordinateSystem = WGS84
        # extract by mask
        if not arcpy.Exists(outRaster):
            extract = arcpy.sa.ExtractByMask(pointid,raster)
            extract.save(outRaster)
            arcpy.BuildPyramids_management(outRaster)
            print "Created " + outRaster
        else:
            pass


# The number of jobs is equal to the number of files
startTime = datetime.now()
print startTime

workspace = r"F:\GPW\fishnets\output_tifs"
arcpy.env.workspace = workspace
rasters = arcpy.ListRasters('*')
for raster in rasters:
    update_rasters(raster)

print datetime.now()-startTime
print "Alyssa and Olena are amazing!"
