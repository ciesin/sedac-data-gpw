# -*- coding: utf-8 -*-
"""
Created on Mon Oct 22 11:10:29 2018

@author: jmills
Validate the sums of the pop count rasters
"""

import arcpy, os, multiprocessing, numpy

def rSum(r):
    message = None
    rName = os.path.basename(r)[:-4]
    arcpy.env.scratchWorkspace = r'\\Dataserver1\gpw\GPW4\Release_411\validation'
    
    try:
        rasterSum = 0
        if rName[-1].isdigit():
            rList = [r.replace("1.asc",str(i)+".asc") for i in range(1,9)]
            for r30 in rList:
                arr = arcpy.RasterToNumPyArray(r30,"","","",0)
                rasterSum += numpy.sum(arr)
        else:
            arr = arcpy.RasterToNumPyArray(r,"","","",0)
            rasterSum = numpy.sum(arr)
        message = "{},{}".format(rName,rasterSum)
    except:
        message = "{} failed".format(rName)
        
    return message
    
def main():
    asciis = r'F:\gpw\v411\ascii'
#    dig = [str(i) for i in range(2,9)]
#    asciiList = [os.path.join(asciis,a) for a in os.listdir(asciis) if a[-4:] == ".asc" and a[-5] not in dig]
    allAsciis = [a for a in os.listdir(asciis) if a[-4:] == ".asc" if "cntm" in a or "count_" in a]
    asciiList = [os.path.join(asciis,a) for a in allAsciis if "30_sec_1" in a]
    asciiList.sort()

    print("Validating {} rasters".format(len(asciiList)))

    pool = multiprocessing.Pool(processes=min([len(asciiList),20]), maxtasksperchild=1)
    results = pool.map(rSum, asciiList)
    for result in results:
        print(result)

    pool.close()
    pool.join()
    print("Script complete")


if __name__ == '__main__':
    main()




