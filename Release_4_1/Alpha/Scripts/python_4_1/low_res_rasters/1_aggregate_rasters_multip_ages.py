#Jane Mills
#4/17/2017
#GPW
#Aggregate land, count, mean admin unit area, and water mask

import arcpy, os, re, multiprocessing, datetime
from arcpy import env
arcpy.CheckOutExtension("Spatial")
scriptTime = datetime.datetime.now()

def aggregate_rasters(rPath):
    r = os.path.basename(rPath)
    env.overwriteOutput = True
    processTime = datetime.datetime.now()
    outFolder = r'D:\gpw\release_4_1\low_res'
    resolutions = ['2pt5_min','15_min','30_min','1_deg']
    scales = ['5','30','60','120']
    returnList = []

    for i in range(4):
        #print i
        res = resolutions[i]
        scale = scales[i]
        extRast = os.path.join(outFolder,'extents','gpw4_extent_'+res+'.tif')
        env.snapRaster = extRast
        #extRaster = arcpy.sa.Raster(extRast)
        #env.extent = extRaster.extent

        outR = os.path.join(outFolder,r[:-4]+'_'+res+'.tif')

        #Add up all count grids and area grids
        if '_cntm' in r or 'areakm' in r:
            arcpy.gp.Aggregate_sa(rPath,outR,scale,"SUM")

    returnList.append("Calculated " + r[:-4])
    return returnList

def main():
    root = r'D:\gpw\release_4_1\merge'

    print "processing"

    env.workspace = root
    rList1 = filter(lambda x: '_dens' not in os.path.basename(x), [os.path.join(root,r) for r in arcpy.ListRasters("*_e_a0*")])
    rList2 = filter(lambda x: '_dens' not in os.path.basename(x), [os.path.join(root,r) for r in arcpy.ListRasters("*_e_atotpopm*")])
    rList3 = filter(lambda x: '_dens' not in os.path.basename(x), [os.path.join(root,r) for r in arcpy.ListRasters("*_e_atotpopf*")])
    rList = rList1 + rList2 + rList3
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


