#Jane Mills
#12/4/17
#GPW
#Aggregate un adjusted data

import arcpy, os, re, multiprocessing, datetime
from arcpy import env
arcpy.CheckOutExtension("Spatial")
scriptTime = datetime.datetime.now()

def aggregate_rasters(rPath):
    extents = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\ancillary\extents'
    landF = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\rasters'
    r = os.path.basename(rPath)
    env.overwriteOutput = True
    env.compression = "LZW"
    processTime = datetime.datetime.now()
    outFolder = r'D:\gpw\release_4_1\global_tifs\processing'
    finalFolder = r'D:\gpw\release_4_1\global_tifs'
    resolutions = ['2pt5_min','15_min','30_min','1_deg']
    scales = ['5','30','60','120']
    returnList = []

    for i in range(4):
        #print i
        res = resolutions[i]
        scale = scales[i]
        extRast = os.path.join(extents,'gpw4_extent_'+res+'.tif')
        env.snapRaster = extRast
        land = os.path.join(landF,'gpw_v4_maskedareakm_'+res+'.tif')
        #extRaster = arcpy.sa.Raster(extRast)
        #env.extent = extRaster.extent

        rName = r.replace("30_sec",res)
        
        aggR = os.path.join(outFolder,rName[:-4]+"_agg.tif")
        divR = os.path.join(outFolder,rName.replace("cntm","dens"))
        arcpy.gp.Aggregate_sa(rPath,aggR,scale,"SUM")
        arcpy.gp.Divide_sa(aggR,land,divR)
        
        finalCount = os.path.join(finalFolder,rName)
        finalDens = os.path.join(finalFolder,rName.replace("cntm","dens"))
        arcpy.CopyRaster_management(aggR,finalCount)
        arcpy.CopyRaster_management(divR,finalDens)

    returnList.append("Calculated " + r[:-4])
    return returnList

def main():
    root = r'D:\gpw\release_4_1\global_tifs'

    print "processing"

    env.workspace = root
    rList = [os.path.join(root,r) for r in arcpy.ListRasters("*_une_*_cntm_*")]
    rList.sort()

    pool = multiprocessing.Pool(processes=10,maxtasksperchild=1)
    results = pool.map(aggregate_rasters, rList)
    for result in results:
        for result2 in result:
            print result2

    pool.close()
    pool.join()
    print "Script Complete in " + str(datetime.datetime.now()-scriptTime)


if __name__ == '__main__':
    main()


