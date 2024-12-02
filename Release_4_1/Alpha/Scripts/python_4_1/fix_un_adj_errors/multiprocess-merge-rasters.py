# Kytt MacManus
# Jane Mills
# 12-4-17
# merge_rasters.py

import arcpy, os, datetime, multiprocessing, socket

def mergeGrids(rasterList):
    startTime = datetime.datetime.now()
    arcpy.CheckOutExtension("SPATIAL")
    year = os.path.basename(rasterList[0])[-13:-9]
    outFolder = r'D:\gpw\release_4_1\global_tifs'
    waterMask = r'D:\gpw\release_4_1\merge\gpw_v4_watermask.tif'
    outRaster = os.path.join(outFolder,'processing','gpw_v4_une_atotpopbt_'+year+'_cntm_30_sec.tif')
    outRaster2 = os.path.join(outFolder,'processing','gpw_v4_une_atotpopbt_'+year+'_cntm_30_sec_setnull.tif')
    copyRaster = os.path.join(outFolder,'gpw_v4_une_atotpopbt_'+year+'_cntm_30_sec.tif')
    # define outExtent
    outExtent = r'\\Dataserver0\gpw\GPW4\Release_4_0\Prod\Gridding\global\ancillary\gpw4_extent.tif'
    arcpy.env.extent = outExtent
    try:
        arcpy.env.compression = "LZW"
        #cellStats = arcpy.sa.CellStatistics(rasterList, "SUM", "DATA")
        #cellStats.save(outRaster)

        arcpy.env.mask = outRaster
        snRaster = SetNull(Raster(waterMask)==0,Raster(cellStats))
        finalRaster = SetNull(Raster(snRaster)<0.0001,snRaster)
        finalRaster.save(outRaster2)
        arcpy.CopyRaster_management(outRaster2,copyRaster)
        arcpy.BuildPyramidsandStatistics_management(copyRaster)
        # success
        return "Processed "+ outRaster
    except:
        return outRaster + " error: " + str(arcpy.GetMessages())

def main():
    print "Processing"
    scriptTime = datetime.datetime.now()

    inWS = r'D:\gpw\release_4_1\country_tifs'

    rasterLists = []
    for year in ['1975','1990','2000','2005','2010','2015','2020']:
        rasterList = []
        for root, dirs, files in os.walk(inWS):
            for f in files:
                if "UNE_" in f and year in f and f.endswith(".tif"):
                    rasterList.append(os.path.join(root,f))
        print str(year) + ": " + str(len(rasterList)) + " rasters to process"
        rasterLists.append(rasterList)

    # multiprocess the data
    pool = multiprocessing.Pool(processes=4,maxtasksperchild=1)
    results = pool.map(mergeGrids, rasterLists)
    for result in results:
        print result
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()
    print "Script complete"
    print str(datetime.datetime.now()-scriptTime)

if __name__ == '__main__':
    main()
