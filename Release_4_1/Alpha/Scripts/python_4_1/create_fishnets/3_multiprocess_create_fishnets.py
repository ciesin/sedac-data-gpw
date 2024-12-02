# multiprocess_create_fishnets.py
# convert pixel id files into vector fishnets

import os
import re
import multiprocessing
import arcpy
 
def update_rasters(raster):
    scratchDir = r"E:\gpw\country\scratch" + os.sep + os.path.basename(raster.lower())[:-8]    
    arcpy.env.scratchWorkspace = scratchDir         
    WGS84 = arcpy.SpatialReference(4326)
    arcpy.env.outputCoordinateSystem = WGS84
    # skip can, chn, usa, and rus
    if os.path.basename(raster.lower())[:-8] == "can" or os.path.basename(raster.lower())[:-8] == "chn" or os.path.basename(raster.lower())[:-8] == "usa" or os.path.basename(raster.lower())[:-8] == "rus":
        pass
    else:
        # create output gdb
        outGDB = r"E:\gpw\country\fishnets" + os.sep + os.path.basename(raster.lower())[:-8] + ".gdb"
        if not arcpy.Exists(outGDB):
            arcpy.CreateFileGDB_management(r"E:\gpw\country\fishnets",os.path.basename(raster.lower())[:-8])
        else:
            pass
        # convert to polygons
        outFishnet = outGDB + os.sep + os.path.basename(raster.lower())[:-8] + "_fishnet"
        if not arcpy.Exists(outFishnet):
            arcpy.RasterToPolygon_conversion(raster,outFishnet,"NO_SIMPLIFY","Value")
        else:
            pass
 
# End update_shapefiles
def main():
   
    # The number of jobs is equal to the number of files
    workspace = r'E:\gpw\country\ids'
    arcpy.env.workspace = workspace
    rasters = arcpy.ListRasters('mwi*.tif*')
    raster_list = [os.path.join(workspace, raster) for raster in rasters]
    print "processing"
    pool = multiprocessing.Pool()
    pool.map(update_rasters, raster_list) 
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()
    # End main
    print "complete"
 
if __name__ == '__main__':
    main()
