# multiprocess_create_fishnets.py
# convert pixel id files into vector fishnets

import os
import re
import multiprocessing
import arcpy
from datetime import datetime
 
def update_rasters(raster):
    scratchDir = r"F:\GPW\fishnets\scratch" + os.sep + os.path.basename(raster.lower())[:-8]
    arcpy.env.scratchWorkspace = scratchDir
    WGS84 = arcpy.SpatialReference(4326)
    arcpy.env.outputCoordinateSystem = WGS84
    
    # create output gdb
    outGDB = r"F:\GPW\fishnets\output_fishnets\tiles" + os.sep + iso + os.sep + os.path.basename(raster.lower())[:-8] + ".gdb"
    if not arcpy.Exists(outGDB):
        arcpy.CreateFileGDB_management(r"F:\GPW\fishnets\output_fishnets\tiles" + os.sep + iso,os.path.basename(raster.lower())[:-8])
    else:
        pass
        # convert to polygons
        outFishnet = outGDB + os.sep + os.path.basename(raster.lower())[:-8] + "_fishnet"
        if not arcpy.Exists(outFishnet):
            arcpy.RasterToPolygon_conversion(raster,outFishnet,"NO_SIMPLIFY","Value")
        else:
            pass

# The number of jobs is equal to the number of files

isos = ['can','rus']
for iso in isos:

    workspace = os.path.join(r"F:\GPW\fishnets\output_tifs_ids\tiles",iso)
    arcpy.env.workspace = workspace
    rasters = arcpy.ListRasters('*')
    for raster in rasters:
        update_rasters(raster)

    startTime = datetime.now()
    print startTime
    print datetime.now()-startTime
    print "Alyssa and Olena are amazing!"

