# -*- coding: utf-8 -*-
"""
Created on Mon Oct 22 11:10:29 2018

@author: jmills
Validate the sums of the pop count rasters
"""

import arcpy, os, multiprocessing
from arcpy.sa import *
arcpy.env.overwriteOutput = True

def rSum(r):
    message = None
    rName = os.path.basename(r)[:-4]
    arcpy.CheckOutExtension("Spatial")
    arcpy.env.scratchWorkspace = r'\\Dataserver1\gpw\GPW4\Release_411\validation'
    outGDB = r'\\Dataserver1\gpw\GPW4\Release_411\validation\validation.gdb'
    
    try:
        rasterSum = 0
        res = "_".join(rName.split("_")[-2:])
        extRast = os.path.join(r'\\Dataserver1\gpw\GPW4\Release_411\ancillary\extents','gpwv411_extent_'+res+'.tif')
        outTable = os.path.join(outGDB,rName)
        if not arcpy.Exists(outTable):
            arcpy.gp.ZonalStatisticsAsTable_sa(extRast, "Value", r, outTable, "DATA", "SUM")
#        else:
#            rows = 0
#            with arcpy.da.SearchCursor(outTable,"SUM") as cursor:
#                for row in cursor:
#                    rows += 1
#            if rows == 0:
#                arcpy.gp.ZonalStatisticsAsTable_sa(extRast, "Value", r, outTable, "DATA", "SUM")

        with arcpy.da.SearchCursor(outTable,"SUM") as cursor:
            for row in cursor:
                rasterSum = row[0]
                    
        message = "{},{}".format(rName,rasterSum)
    except:
        message = "{} failed".format(rName)
        
    return message
    
def main():
    oldRasters = r'\\Dataserver1\gpw\GPW4\Release_4_1\Alpha\Gridding\rasters'
    arcpy.env.workspace = oldRasters
    rList = arcpy.ListRasters("*demographic*cntm*30_sec*") + arcpy.ListRasters("*population_count*30_sec*")
    rList.sort()
    newRasters = r'\\Dataserver1\gpw\GPW4\Release_411\rasters_30sec'
    lowRes = r'\\Dataserver1\gpw\GPW4\Release_411\rasters_lowres'
    resolutions = ['2pt5_min','15_min','30_min','1_deg']
    
    outGDB = r'\\Dataserver1\gpw\GPW4\Release_411\validation\validation.gdb'
    arcpy.env.workspace = outGDB
    tableList = arcpy.ListTables()
    
    oldRast = [os.path.join(oldRasters,r) for r in rList if r[:-4] not in tableList]
    newRast = [os.path.join(newRasters,r.replace("rev10","rev11")) for r in rList if r.replace("rev10","rev11")[:-4] not in tableList]
    lowResRasts = [os.path.join(lowRes,r.replace("rev10","rev11").replace("30_sec",res)) for res in resolutions for r in rList if r.replace("rev10","rev11").replace("30_sec",res)[:-4] not in tableList]

    rasterList = lowResRasts + newRast + oldRast
    rasterList.sort()

    print("Validating {} rasters".format(len(rasterList)))

    pool = multiprocessing.Pool(processes=min([len(rasterList),15]), maxtasksperchild=1)
    results = pool.map(rSum, rasterList)
    for result in results:
        print(result)

    pool.close()
    pool.join()
    print("Script complete")


if __name__ == '__main__':
    main()




