#Jane Mills
#4/17/2017
#GPW
#Set null any negative values - NoData values aren't defined which is throwing off all my scripts

import arcpy, os, re, multiprocessing, datetime
from arcpy import env
arcpy.CheckOutExtension("Spatial")
scriptTime = datetime.datetime.now()

def fix_rasters(rPath):
    r = os.path.basename(rPath)
    env.overwriteOutput = True
    processTime = datetime.datetime.now()
    outFolder = r'F:\GPW\rasters_4_1\high_res'
    returnList = []

    outR = os.path.join(outFolder,r)
    null = os.path.join(outFolder,r[7:-10]+'null.tif')
    
    arcpy.gp.SetNull_sa(rPath,rPath,null,"VALUE < -.01")
    #can't translate if it's not on disk
    os.system("gdal_translate -ot Float32 -co COMPRESS=LZW -of GTiff " + null + " " +  outR)

    arcpy.Delete_management(null)

    returnList.append("Calculated " + r[7:-10])
    return returnList

def main():
    root = r'F:\GPW\rasters_4_1\orig'

    print "processing"

    env.workspace = root
    rList = [os.path.join(root,raster) for raster in arcpy.ListRasters()]
    rList.sort()

    #for r in rList[:10]:
    #    print os.path.basename(r)
    #    fix_rasters(r)

    pool = multiprocessing.Pool(processes=5,maxtasksperchild=1)
    results = pool.map(fix_rasters, rList)
    for result in results:
        for result2 in result:
            print result2

    pool.close()
    pool.join()
    
    print "Script Complete in " + str(datetime.datetime.now()-scriptTime)


if __name__ == '__main__':
    main()


