# -*- coding: utf-8 -*-
"""
Created on Mon Oct 22 11:10:29 2018

@author: jmills
Validate the sums of the pop count rasters
"""

import arcpy, os, numpy, multiprocessing
arcpy.env.overwriteOutput = True

def rSum(r):
    message = None
    oldRasters = r'\\Dataserver1\gpw\GPW4\Release_4_1\Alpha\Gridding\rasters'
    newRasters = r'\\Dataserver1\gpw\GPW4\Release_411\rasters_30sec'
    lowRes = r'\\Dataserver1\gpw\GPW4\Release_411\rasters_lowres'
    resolutions = ['2pt5_min','15_min','30_min','1_deg']
    arcpy.env.scratchWorkspace = r'\\Dataserver1\gpw\GPW4\Release_411\validation'
    
    oldRast = os.path.join(oldRasters,r)
    newRast = os.path.join(newRasters,r.replace("rev10","rev11"))
    lowResRasts = [os.path.join(lowRes,r.replace("rev10","rev11").replace("30_sec",res)) for res in resolutions]
    
    rasterList = [oldRast] + [newRast] + lowResRasts
    sums = [0]*6
    
    try:
        for i in range(2):
            llcorners = [arcpy.Point(-180, 0), arcpy.Point(-90,0), arcpy.Point(0,0), arcpy.Point(90,0),
                         arcpy.Point(-180, -90), arcpy.Point(-90,-90), arcpy.Point(0,-90), arcpy.Point(90,-90)]
            rast = rasterList[i]
            n = 10800
            rSum = 0
            for j in range(8):
                ll = llcorners[j]
                rArr = arcpy.RasterToNumPyArray(rast, ll, n, n, 0)
                rSum += numpy.sum(rArr)
                
            sums[i] = rSum
        
        for i in range(2,6):
            rast = rasterList[i]
            rArr = arcpy.RasterToNumPyArray(rast,nodata_to_value=0)
            sums[i] = numpy.sum(rArr)
        
        printSums = [str(int(s)) for s in sums]
        
        message = "{},{}".format(r,",".join(printSums))
    except:
        message = "{} failed".format(r)
        
    return message
    
def main():
    oldRasters = r'\\Dataserver1\gpw\GPW4\Release_4_1\Alpha\Gridding\rasters'
    arcpy.env.workspace = oldRasters
    #rList = arcpy.ListRasters("*demographic*025_029*cntm*30_sec*")
    rList = arcpy.ListRasters("*demographic*cntm*30_sec*") + arcpy.ListRasters("*population_count*30_sec*")
    rList.sort()
    rList = rList[:5]

    print("Validating {} rasters".format(len(rList)))

    pool = multiprocessing.Pool(processes=15, maxtasksperchild=1)
    results = pool.map(rSum, rList)
    for result in results:
        print(result)

    pool.close()
    pool.join()
    print("Script complete")


if __name__ == '__main__':
    main()




