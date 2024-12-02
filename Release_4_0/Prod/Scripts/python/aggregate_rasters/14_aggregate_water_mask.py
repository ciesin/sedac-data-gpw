#Jane Mills
#GPW
#Aggregate the water mask

import arcpy, os
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")

def aggregate_water(resolution,scale):
    inRaster = r'F:\GPW\aggregate_rasters\global_tifs\gpw-v4-data-quality-indicators\gpw-v4-data-quality-indicators_water-mask.tif'
    outFolder = os.path.join(r'F:\GPW\aggregate_rasters\rasters_other_resolution',resolution,'gpw-v4-data-quality-indicators')

    outRaster1 = os.path.join(outFolder,'gpw-v4-data-quality-indicators_water-mask_aggregate.tif')
    outRaster2 = os.path.join(outFolder,'gpw-v4-data-quality-indicators_water-mask.tif')

    arcpy.gp.Aggregate_sa(raster,outRaster1,scale,"SUM")
    arcpy.gp.Reclassify_sa(inR, "Value", "0 0;0 9801 1",outR, "NODATA")
    

aggregate_water('2_5_minute','5')
print("finished 2.5 minute")

aggregate_water('0_25_degree','30')
print("finished 0.25 degree")

aggregate_water('0_5_degree','60')
print("finished 0.5 degree")

aggregate_water('1_degree','120')
print("finished 1 degree")
