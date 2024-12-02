# multiprocess_extract_and_convert
# extract pointids to country mask 
## NOTE THIS CODE WAS RUN ON DEVSEDARC VM PREVIOUSLY
## PATH MAY NEED TO BE UPDATED

import os
import re
import multiprocessing
import arcpy
 
def update_rasters(raster):
    outRaster = r"E:\gpw\country\updates\twn" + os.sep + os.path.basename(raster.lower())[:-4] + "_ids"
    if arcpy.Exists(outRaster):
        print outRaster + " already exists"
    else:
        scratchDir = r"E:\gpw\country\scratch" + os.sep + os.path.basename(raster.lower())[:-4]
        if not arcpy.Exists(scratchDir):
            os.mkdir(scratchDir)
        arcpy.env.scratchWorkspace = scratchDir         
        pointid = r"E:\gpw\country\data\gpw4_30second_ids.tif" # it is important to extract from this layer
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
    workspace = r"E:\gpw\country\updates\twn"
    arcpy.env.workspace = workspace
    rasters = arcpy.ListRasters('abw*')
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
