#Jane Mills
#3/9/17
#summarize rasters and compare to tables

import arcpy, os, csv,sys
from arcpy import env
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")
env.overwriteOutput=True
rootFolder = r'D:\gpw\release_4_1\country_tifs'
gridding = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\boundaries\gridding_boundaries_4_1.gdb'
extent = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\fishnets\gpw4_extent.tif'
outGDB = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\validation\scratch.gdb'

csvPath = open(r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Scripts\python_4_1\validation\country_counts_6_13.csv',"wb")
csvFile = csv.writer(csvPath)
csvFile.writerow(("ISO","raster","raster_sum","raster_max","raster_min","raster_std","table_count"))
isoList = os.listdir(rootFolder)
isoList.sort()

env.workspace = gridding
fcList = [os.path.join(gridding,fc) for fc in arcpy.ListFeatureClasses()]

env.overwriteOutput = True

for iso in isoList:
    print iso
    isoPath = os.path.join(rootFolder,iso)
    env.workspace = isoPath
    rasterList = [os.path.join(isoPath,r) for r in arcpy.ListRasters("*CNTM*")]
    rasterList.sort()
    if len(rasterList) == 0:
        tileList = os.listdir(isoPath)
        tileList.sort()
        for tile in tileList:
            tilePath = os.path.join(isoPath,tile)
            env.workspace = tilePath
            rasterList = [os.path.join(tilePath,r) for r in arcpy.ListRasters("*CNTM*")]
            rasterList.sort()
    else:
        tile = iso
    for raster in rasterList:
        print os.path.basename(raster)
        try:
            fieldName = os.path.basename(raster)[len(tile)+1:-9]
            outTable = os.path.join(outGDB,'temp')
            #summarize raster
            arcpy.gp.ZonalStatisticsAsTable_sa(extent,"Value",raster,outTable,"DATA","ALL")
            rCount = 0
            rmax = 0
            rmin = 0
            rstd = 0
            with arcpy.da.SearchCursor(outTable,['SUM','MIN','MAX','STD']) as cursor:
                for row in cursor:
                    rCount = row[0]
                    rmin = row[1]
                    rmax = row[2]
                    rstd = row[3]

            #summarize table
            tCount = "Not in table"
            bounds = filter(lambda x: os.path.basename(x)[:3] == iso, fcList)
            if fieldName in [f.name for f in arcpy.ListFields(bounds[0])]:
                tCount = 0
                with arcpy.da.SearchCursor(bounds[0],fieldName,fieldName+' > 0') as cursor:
                    for row in cursor:
                        tCount += row[0]
            csvFile.writerow((iso,fieldName,str(rCount),str(rmax),str(rmin),str(rstd),str(tCount)))
        except:
            print "failed"

csvPath.close()
print "done"

