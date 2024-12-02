#Jane Mills
#7/14/16
#GPW
#Aggregate the mean admin unit area grid

import arcpy, os
from arcpy import env

arcpy.CheckOutExtension("Spatial")

def aggregate_rasters(rasterFolder):
    outRoot = r'F:\GPW\aggregate_rasters\rasters_other_resolution'
    resolutions = ['0_25_degree','0_5_degree','1_degree','2_5_minute']
    scales = ['30','60','120','5']
    
    inRaster = r'F:\GPW\aggregate_rasters\global_tifs\gpw-v4-data-quality-indicators\gpw-v4-data-quality-indicators_mean-administrative-unit-area.tif'

    for i in range(4):
        res = resolutions[i]
        scale = scales[i]
        outFolder = os.path.join(outRoot,res,rasterFolder)
        outRaster = os.path.join(outFolder,'gpw-v4-data-quality-indicators_mean-administrative-unit-area.tif')

        os.mkdir(outFolder)

        arcpy.gp.Aggregate_sa(inRaster,outRaster,scale,"MEAN")


aggregate_rasters('gpw-v4-data-quality-indicators')
print("finished data quality")
