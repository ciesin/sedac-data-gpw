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

resolutions = ['2pt5_min','15_min','30_min','1_deg']

#check high res rasters
env.workspace = highRes
rasterList = arcpy.ListRasters("*cntm*")
#ids = 'gpw_v4_national_identifier.tif'
ext = os.path.join(lowRes,'extents','gpw4_extent_30_sec.tif')
print "30_sec"

#for raster in rasterList:
#    print raster
#    outTable = os.path.join(outGDB,raster[:-4]+"_30_sec")
#    arcpy.gp.ZonalStatisticsAsTable_sa(ext,"VALUE",raster,outTable,"DATA","SUM")

print "finished"

#check low res rasters
env.workspace = lowRes
env.overwriteOutput = True
for res in resolutions:
    print res
    #ids = 'gpw_v4_national_identifier_'+res+'.tif'
    ext = os.path.join(lowRes,'extents','gpw4_extent_'+res+'.tif')
    rasterList = arcpy.ListRasters("*cntm*"+res+"*")
    for raster in rasterList:
        print raster
        outTable = os.path.join(outGDB,raster[:-4])
        arcpy.gp.ZonalStatisticsAsTable_sa(ext,"VALUE",raster,outTable,"DATA","SUM")

    print "finished"

print "done"


