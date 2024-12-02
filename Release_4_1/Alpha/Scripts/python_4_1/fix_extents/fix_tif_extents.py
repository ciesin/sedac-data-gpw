#Jane Mills
#GPW
#fix the extents of all of our rasters

import arcpy, os, re, multiprocessing
from arcpy import env
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True

def fix_extent(raster):
    returnList = []
    extents = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\ancillary\extents'
    outFolder = r'F:\gpw\gpw4_rev10_fixed_extents\rasters'
    outFolder1 = r'F:\gpw\gpw4_rev10_fixed_extents\scratch'

    rName = os.path.basename(raster)

    if "30_sec" in rName:
        extRaster = os.path.join(extents,'gpw4_extent_30_sec.tif')
    elif "2pt5_min" in rName:
        extRaster = os.path.join(extents,'gpw4_extent_2pt5_min.tif')
    elif "15_min" in rName:
        extRaster = os.path.join(extents,'gpw4_extent_15_min.tif')
    elif "30_min" in rName:
        extRaster = os.path.join(extents,'gpw4_extent_30_min.tif')
    elif "1_deg" in rName:
        extRaster = os.path.join(extents,'gpw4_extent_1_deg.tif')

    env.snapRaster = extRaster
    extRast = arcpy.sa.Raster(extRaster)
    env.extent = extRast.extent
    env.compression = "LZW"

    outR = os.path.join(outFolder,rName)
    outRtemp = os.path.join(outFolder1,rName[:-4]+"_temp.tif")
    
    arcpy.gp.Con_sa(raster,raster,outRtemp,"","")
    arcpy.CopyRaster_management(outRtemp,outR)
    arcpy.Delete_management(outRtemp)

    returnList.append("Calculated " + rName)
    return returnList


def main():
    root = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\rasters_corrected_un_adj'

    print "processing"

    env.workspace = root
    rList = [os.path.join(root,r) for r in arcpy.ListRasters()]
    rList.sort()

    pool = multiprocessing.Pool(processes=10,maxtasksperchild=1)
    results = pool.map(fix_extent, rList)
    for result in results:
        for result2 in result:
            print result2

    pool.close()
    pool.join()
    print "Script Complete"


if __name__ == '__main__':
    main()
