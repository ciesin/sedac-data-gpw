# multiprocess_create_fishnets.py
# convert pixel id files into vector fishnets

import os
import re
import multiprocessing
import arcpy
 
def update_rasters(raster):  
    #arcpy.management.CalculateStatistics(raster)  
    iso = os.path.basename(raster).split("_")[0]
    scratchDir = r"F:\gpwv5\fishnet\scratch" + os.sep + os.path.basename(raster.lower())[:-8]    
    arcpy.env.scratchWorkspace = scratchDir         
    WGS84 = arcpy.SpatialReference(4326)
    arcpy.env.outputCoordinateSystem = WGS84
    # create output gdb
    outGDB = r"F:\gpwv5\fishnet\gpw5_fishnets\15_second" + os.sep + iso +"_fishnet.gdb"
    if not arcpy.Exists(outGDB):
        arcpy.CreateFileGDB_management(r"F:\gpwv5\fishnet\gpw5_fishnets\15_second",iso+"_fishnet")
    else:
        pass
    # convert to polygons
    inFramework = r"F:\gpwv5\fishnet\framework_polygons\framework_shps"+ os.sep + iso +".shp"
    frameworkLyr = iso+"frame"
    tmpFishnet = "in_memory" + os.sep + iso + "_fishnet"
    tmpFishnetLyr = iso+"lyr"
    outFishnet = outGDB + os.sep + iso + "_fishnet"
    if not arcpy.Exists(outFishnet):
        try:
            # arcpy.conversion.RasterToPolygon(raster,outFishnet,"NO_SIMPLIFY","Value")
            # convert to polygon in memory
            # arcpy.management.AddField(raster,"VALUETEXT","TEXT")
            # arcpy.management.CalculateField(raster,"VALUETEXT","!Value!","PYTHON")
            arcpy.RasterToPolygon_conversion(raster,tmpFishnet,"NO_SIMPLIFY","Value")
            ##arcpy.RasterToPolygon_conversion(raster,tmpFishnet,"NO_SIMPLIFY","Value")
            # create feature layers
            arcpy.MakeFeatureLayer_management(inFramework,frameworkLyr)
            arcpy.MakeFeatureLayer_management(tmpFishnet,tmpFishnetLyr)
            # select by location
            arcpy.SelectLayerByLocation_management(tmpFishnetLyr,"INTERSECT",frameworkLyr,"#","NEW_SELECTION")
            # write to disk
            arcpy.FeatureClassToFeatureClass_conversion(tmpFishnetLyr,outGDB,iso+"_fishnet") 
            # add and calculate ID field          
            arcpy.management.AddField(outFishnet,"PIXELID","DOUBLE")
            # arcpy.management.CalculateField(outFishnet,"PIXELID","!VALUETEXT!","PYTHON")
            arcpy.management.CalculateField(outFishnet,"PIXELID","!gridcode!","PYTHON")
            return("Created "+outFishnet)
        except:
            return("Failure to process "+raster+" "+arcpy.GetMessages())
    else:
        return(outFishnet + " already exists")
 
# End update_shapefiles
def main():   
    # The number of jobs is equal to the number of files
    workspace = r'F:\gpwv5\fishnet\pointid_rasters\15_second'
    arcpy.env.workspace = workspace
    rasters = arcpy.ListRasters('GBNIR*')
    # for raster in rasters:                
    #     print(update_rasters(raster))             
    raster_list = [os.path.join(workspace, raster) for raster in rasters]
    print("processing ", len(raster_list))
    pool = multiprocessing.Pool(processes=1,maxtasksperchild=1)     
    results = pool.map(update_rasters, raster_list)
    for result in results:
        print(result)  
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()
    # End main
    print("Complete")
 
if __name__ == '__main__':
    main()
