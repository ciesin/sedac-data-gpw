#Jane Mills
#3/9/17
#summarize rasters and compare to tables

import arcpy, os, csv,sys
from arcpy import env
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")
env.overwriteOutput=True
rootFolder = r'D:\gpw\release_4_1\country_tifs'
tableRoot = r'D:\gpw\release_4_1\process'
extent = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\fishnets\gpw4_extent.tif'
outGDB = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\validation\zonal_stats.gdb'

csvPath = open(r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Scripts\python_4_1\validation\country_counts.csv',"wb")
csvFile = csv.writer(csvPath)
csvFile.writerow(("ISO","raster","raster_sum","raster_max","raster_min","raster_std","table_count"))
isoList = os.listdir(rootFolder)
isoList.sort()

for iso in isoList:
    if len(iso) == 3:
        print iso
        isoPath = os.path.join(rootFolder,iso)
        env.workspace = isoPath
        rasterList = arcpy.ListRasters("*CNTM*")
        rasterList.sort()
        for raster in rasterList:
            print raster
            rasterPath = os.path.join(isoPath,raster)
            fieldName = raster[len(iso)+1:-9]
            outTable = 'in_memory' + os.sep + raster[:-9])
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
            tableGDB = tableRoot + os.sep + iso + '.gdb'
            env.workspace = tableGDB
            tablePath = arcpy.ListTables("*_estimates")[0]
            with arcpy.da.SearchCursor(tablePath,fieldName,fieldName+' > 0') as cursor:
                for row in cursor:
                    tCount += row[0]
##            print 'write'
            csvFile.writerow((iso,fieldName,str(rCount),str(rmax),str(rmin),str(rstd),str(tCount)))
##            print (iso,fieldName,rCount,rmax,rmin,rstd,tCount)
##            break            
##        break
    else:
        pass
del csvFile
csvPath.close()
print "done"

