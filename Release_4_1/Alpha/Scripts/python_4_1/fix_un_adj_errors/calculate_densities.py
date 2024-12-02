#Jane Mills
#4/17/2017
#GPW
#Divide the counts by the land area to get the densities

import arcpy, os
from arcpy import env
env.overwriteOutput = True

arcpy.CheckOutExtension("Spatial")

outFolder = r'D:\gpw\release_4_1\global_tifs'
land = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\rasters\gpw_v4_maskedareakm_30_sec.tif'

env.workspace = outFolder

rList = arcpy.ListRasters()
rList.sort()

for r in rList:
    print r
    outR = r.replace('_cntm_','_dens_')
    outR1 = os.path.join(outFolder,'processing',outR)
    arcpy.env.compression = "LZW"
    
    arcpy.gp.Divide_sa(r,land,outR1)
    arcpy.CopyRaster_management(outR1,outR)


