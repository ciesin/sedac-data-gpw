#Jane Mills
#7/13/16
#GPW
#Validate the grids

import arcpy, os, csv
from arcpy import env

arcpy.CheckOutExtension("Spatial")
env.overwriteOutput = True

highRes = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\rasters\high_res'
lowRes = r'D:\gpw\release_4_1\low_res'
outGDB = os.path.join(lowRes,'scratch','zonal_stats.gdb')
#arcpy.CreateFileGDB_management(os.path.join(lowRes,'scratch'),'zonal_stats.gdb')

resolutions = ['2pt5_min','15_min','30_min','1_deg']

csvPath = open(os.path.join(lowRes,'scratch','counts_rasters.csv'),"wb")
csvFile = csv.writer(csvPath)
csvFile.writerow(("ISO","raster","raster_sum"))

#check high res rasters
##env.workspace = highRes
##rasterList = arcpy.ListRasters("*cntm*")
##ids = 'gpw_v4_national_identifier.tif'
##print "30_sec"
##
##for raster in rasterList:
##    outTable = os.path.join(outGDB,'temp')
##    arcpy.gp.ZonalStatisticsAsTable_sa(ids,"ISOCODE",raster,outTable,"DATA","SUM")
##    with arcpy.da.SearchCursor(outTable,['ISOCODE','SUM']) as cursor:
##        for row in cursor:
##            csvFile.writerow((row[0],raster,row[1]))
##
##print "finished"

#check low res rasters
env.workspace = lowRes
env.overwriteOutput = True
for res in resolutions:
    print res
    ids = 'gpw_v4_national_identifier_'+res+'.tif'
    rasterList = arcpy.ListRasters("*cntm*"+res+"*")
    for raster in rasterList:
        outTable = os.path.join(outGDB,'temp')
        arcpy.gp.ZonalStatisticsAsTable_sa(ids,"ISOCODE",raster,outTable,"DATA","SUM")
        with arcpy.da.SearchCursor(outTable,['ISOCODE','SUM']) as cursor:
            for row in cursor:
                csvFile.writerow((row[0],raster,row[1]))

    print "finished"

print "done"


