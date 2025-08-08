# multiprocess_extract_and_convert
# extract pointids to country mask and convert to points

import os
import re
import multiprocessing
import arcpy
 
def update_rasters(raster):
    outRaster = r"F:\gpwv5\fishnet\pointid_rasters\15_second" + os.sep + os.path.basename(raster.lower())[:-4] + "_ids.tif"
    if arcpy.Exists(outRaster):
        return(outRaster + " already exists")
    else:
        scratchDir = r"F:\gpwv5\fishnet\scratch" + os.sep + os.path.basename(raster.lower())[:-4]
        if not arcpy.Exists(scratchDir):
            os.mkdir(scratchDir)
        arcpy.env.scratchWorkspace = scratchDir         
        pointid = r"F:\gpwv5\fishnet\pixel_ids\global_15_second_ids_v2.tif"
        arcpy.CheckOutExtension("Spatial")         
        WGS84 = arcpy.SpatialReference(4326)
        arcpy.env.outputCoordinateSystem = WGS84
        arcpy.env.compression="LZW"
        # extract by mask
        if not arcpy.Exists(outRaster):
            extract = arcpy.sa.ExtractByMask(pointid, raster)
            extract = arcpy.sa.Int(extract)
            extract.save(outRaster)
            arcpy.BuildPyramids_management(outRaster)
            return("Created " + outRaster)
        else:
            return(outRaster + " already exists")
    ##    # convert to points
    ##    outPoints = r"E:\gpw\country\points" + os.sep + os.path.basename(raster.lower())[:-4] + "_points.shp"
    ##    if not arcpy.Exists(outPoints):
    ##        arcpy.RasterToPoint_conversion(outRaster,outPoints,"Value")
    ##    else:
    ##        pass
 
# End update_shapefiles
def main():   
    # The number of jobs is equal to the number of files
    workspace = r'F:\gpwv5\fishnet\framework_rasters\15_second'
    arcpy.env.workspace = workspace
    rasters = arcpy.ListRasters('*')
    # for raster in rasters:
    #     update_rasters(raster)
    raster_list = [os.path.join(workspace, raster) for raster in rasters]
    print("processing")
    pool = multiprocessing.Pool(processes=1,maxtasksperchild=1)     
    results = pool.map(update_rasters, raster_list)
    for result in results:
        print(result) 
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()
    # End main
    print("complete")
 
if __name__ == '__main__':
    main()
