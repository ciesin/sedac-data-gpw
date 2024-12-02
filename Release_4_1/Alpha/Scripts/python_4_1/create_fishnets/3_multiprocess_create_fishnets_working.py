# multiprocess_create_fishnets.py
# convert pixel id files into vector fishnets

import os
import re
import multiprocessing
import arcpy
 
def update_rasters(raster):
    scratchDir = r"F:\GPW\fishnets\scratch" + os.sep + os.path.basename(raster.lower())[:-4]    
    arcpy.env.scratchWorkspace = scratchDir
    WGS84 = arcpy.SpatialReference(4326)
    arcpy.env.outputCoordinateSystem = WGS84
    # skip can, usa, and rus
    if os.path.basename(raster.lower())[:-4] == "can" or os.path.basename(raster.lower())[:-4] == "usa" or os.path.basename(raster.lower())[:-4] == "rus":
        pass
    else:
        # create output gdb
        outGDB = r"F:\GPW\fishnets\output_fishnets" + os.sep + os.path.basename(raster.lower())[:-4] + ".gdb"
        if not arcpy.Exists(outGDB):
            arcpy.CreateFileGDB_management(r"F:\GPW\fishnets\output_fishnets",os.path.basename(raster.lower())[:-4])
        else:
            pass
        # convert to polygons
        outFishnet = outGDB + os.sep + os.path.basename(raster.lower())[:-4] + "_fishnet"
        if not arcpy.Exists(outFishnet):
            arcpy.RasterToPolygon_conversion(raster,outFishnet,"NO_SIMPLIFY","Value")
        else:
            pass
 
# End update_shapefiles
def main():
   
    # The number of jobs is equal to the number of files
    workspace = r'F:\GPW\fishnets\output_tifs_ids'
    arcpy.env.workspace = workspace
    rasters = arcpy.ListRasters('*')
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

print "DONE!"
