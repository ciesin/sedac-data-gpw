#Jane Mills
#3/9/17
#summarize rasters and compare to tables

import arcpy, os, numpy, csv
from arcpy import env
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")

rootFolder = r'F:\gpw\release_4_1\country_tifs'
tableRoot = r'F:\gpw\release_4_1\process'
extent = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\fishnets\gpw4_extent.tif'
outGDB = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\validation\tiled_zonal_stats.gdb'

csvPath = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Scripts\python_4_1\validation\tiled_country_counts_2.csv'
csvFile = csv.writer(open(csvPath,"wb"))
csvFile.writerow(["ISO","tile","raster","raster_sum","raster_max","raster_min","raster_std","table_count"])

isoList = os.listdir(rootFolder)
isoList.sort()

for iso in isoList:
    if len(iso) == 3:
        print iso
        isoPath = os.path.join(rootFolder,iso)

        tileList = os.listdir(isoPath)
        tileList.sort()

        for tile in tileList:
            tilePath = os.path.join(isoPath,tile)

            tablegdb = os.path.join(tableRoot,tile+'.gdb')
            env.workspace = tablegdb

            table = arcpy.ListTables("*estimates")[0]
            tablePath = os.path.join(tablegdb,table)
            
            env.workspace = tilePath

            rasterList = arcpy.ListRasters("*CNTM*")
            rasterList.sort()

            for raster in rasterList:
                print raster
                rasterPath = os.path.join(tilePath,raster)
                fieldName = raster[len(tile)+1:-9]

                outTable = os.path.join(outGDB,raster[:-9])

                #summarize raster
                arcpy.gp.ZonalStatisticsAsTable_sa(extent,"Value",rasterPath,outTable,"DATA","ALL")

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
                tCount = 0
                with arcpy.da.SearchCursor(tablePath,fieldName,fieldName+' > 0') as cursor:
                    for row in cursor:
                        tCount += row[0]

                csvFile.writerow([iso,tile,fieldName,rCount,rmax,rmin,rstd,tCount])

    else:
        pass

print "done"

