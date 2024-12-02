#Jane Mills
#7/13/16
#GPW
#Validate the grids

import arcpy, os, csv
from arcpy import env

arcpy.CheckOutExtension("Spatial")

outGDB = r'D:\gpw\release_4_1\low_res\scratch\zonal_stats.gdb'
env.workspace = outGDB
tableList = arcpy.ListTables()
tableList.sort()

csvPath = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Scripts\python_4_1\low_res_rasters\counts_rasters.csv'
csvFile = csv.writer(open(csvPath,"wb"))
csvFile.writerow(("raster","raster_sum"))

for table in tableList:
    print table
    with arcpy.da.SearchCursor(table,'SUM') as cursor:
        for row in cursor:
            csvFile.writerow((table,row[0]))

print "finished"

