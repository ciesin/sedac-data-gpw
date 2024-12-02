#Jane Mills
#3/9/17
#summarize rasters and compare to tables

import arcpy, os, numpy, csv
from arcpy import env

rootFolder = r'F:\gpw\release_4_1\country_tifs'
tableRoot = r'F:\gpw\release_4_1\process'

csvPath = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Scripts\python_4_1\validation\tiled_country_counts.csv'
csvFile = csv.writer(open(csvPath,"wb"))
csvFile.writerow(["ISO","tile","raster","raster_sum","raster_max","raster_min","table_count"])

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

                #summarize raster
                rCount = 0
                rmax = 0
                rmin = 0
                arr = arcpy.RasterToNumPyArray(rasterPath,nodata_to_value=0)
                rCount = numpy.sum(arr)
                rmax = numpy.amax(arr)
                rmin = numpy.amin(arr)

                #summarize table
                tCount = 0
                with arcpy.da.SearchCursor(tablePath,fieldName,fieldName+' > 0') as cursor:
                    for row in cursor:
                        tCount += row[0]

                csvFile.writerow([iso,tile,fieldName,rCount,rmax,rmin,tCount])

    else:
        pass

print "done"

