#Jane Mills
#3/9/17
#summarize rasters and compare to tables

import arcpy, os, csv,sys
from arcpy import env
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")

arcpy.env.overwriteOutput = True

root = r'D:\gpw\release_4_1\country_tifs'
outGDB = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\validation\scratch.gdb'
extent = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\ancillary\gpw4_extent.tif'

isoList = ['blr','bra','chl','cpv','cub','cyp','ggy','jey','lao','lca','mmr','phl','prk','sau','ssd','uga']

for iso in isoList:
    print iso
    inFolder = os.path.join(root,iso)

    if iso == "bra":
        subFolders = os.listdir(inFolder)
        for sub in subFolders:
            print sub
            subPath = os.path.join(inFolder,sub)
            arcpy.env.workspace = subPath
            rasterList = arcpy.ListRasters("*_UNE_ATOTPOPBT*")
            rasterList.sort()

            for r in rasterList:
                print r
                outTable = os.path.join(outGDB,'temp')
                arcpy.gp.ZonalStatisticsAsTable_sa(extent,"Value",r,outTable,"DATA","SUM")
                rsum = 0
                with arcpy.da.SearchCursor(outTable,'SUM') as cursor:
                    for row in cursor:
                        rsum += row[0]
                print rsum


    else:
        arcpy.env.workspace = inFolder
        rasterList = arcpy.ListRasters("*_UNE_ATOTPOPBT*")
        rasterList.sort()

        for r in rasterList:
            print r
            outTable = os.path.join(outGDB,'temp')
            arcpy.gp.ZonalStatisticsAsTable_sa(extent,"Value",r,outTable,"DATA","SUM")
            rsum = 0
            with arcpy.da.SearchCursor(outTable,'SUM') as cursor:
                for row in cursor:
                    rsum += row[0]
            print rsum

print "done"

