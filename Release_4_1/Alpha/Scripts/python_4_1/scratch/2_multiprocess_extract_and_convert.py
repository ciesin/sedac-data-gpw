# multiprocess_extract_and_convert
# extract pointids to country mask 
## NOTE THIS CODE WAS RUN ON DEVSEDARC VM PREVIOUSLY
## PATH MAY NEED TO BE UPDATED

import os
import re
import multiprocessing
import arcpy
 
def update_rasters(raster):
    outRaster = r"D:\gpw\release_4_1\scratch" + os.sep + os.path.basename(raster.lower())[:-4] + "_ids.tif"
    if arcpy.Exists(outRaster):
        print outRaster + " already exists"
    else:
##        scratchDir = r"D:\gpw\release_4_1\scratch" + os.sep + os.path.basename(raster.lower())[:-4]
##        if not arcpy.Exists(scratchDir):
##            os.mkdir(scratchDir)
##        arcpy.env.scratchWorkspace = scratchDir         
        pointid = r"\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Ancillary\global_30_second_ids.tif" # it is important to extract from this layer
        arcpy.CheckOutExtension("Spatial")
         
        WGS84 = arcpy.SpatialReference(4326)
        arcpy.env.outputCoordinateSystem = WGS84
        # extract by mask
        if not arcpy.Exists(outRaster):
            extract = arcpy.sa.ExtractByMask(pointid, raster)
            extract.save(outRaster)
            arcpy.BuildPyramids_management(outRaster)
            print "Created " + outRaster
        else:
            pass
    ## NOT NEEDED FOR GPW RIGHT NOW
    ##    # convert to points
    ##    outPoints = r"E:\gpw\country\points" + os.sep + os.path.basename(raster.lower())[:-4] + "_points.shp"
    ##    if not arcpy.Exists(outPoints):
    ##        arcpy.RasterToPoint_conversion(outRaster,outPoints,"Value")
    ##    else:
    ##        pass
 
# End update_shapefiles
def main():
   
    # The number of jobs is equal to the number of files
    workspace = r"D:\gpw\release_4_1\scratch"
    arcpy.env.workspace = workspace
    rasters = arcpy.ListRasters('*black_sea*')
    for raster in rasters:
        update_rasters(raster)
##    raster_list = [os.path.join(workspace, raster) for raster in rasters]
##    print "processing"
##    pool = multiprocessing.Pool(processes=2,maxtasksperchild=1)
##    pool.map(update_rasters, raster_list) 
##    # Synchronize the main process with the job processes to
##    # ensure proper cleanup.
##    pool.close()
##    pool.join()
##    # End main
    print "complete"
 
if __name__ == '__main__':
    main()
