#Jane Mills
#7/12/16
#GPW
#Aggregate the land and population rasters to 2.5 minutes and 1 degree

import arcpy, os
from arcpy import env

arcpy.CheckOutExtension("Spatial")

def aggregate_rasters(rasterFolder):
    folderName = os.path.basename(rasterFolder)
    outRoot = r'F:\GPW\aggregate_rasters\rasters_other_resolution'
    outFolder1 = os.path.join(outRoot,'1_degree',folderName)
    outFolder25 = os.path.join(outRoot,'2_5_minute',folderName)

    os.mkdir(outFolder1)
    os.mkdir(outFolder25)

    env.workspace = rasterFolder
    rasterList = arcpy.ListRasters()

    for raster in rasterList:
        outRaster1 = os.path.join(outFolder1,raster)
        outRaster25 = os.path.join(outFolder25,raster)
        print(raster)
        
        arcpy.gp.Aggregate_sa(raster,outRaster25,"5","SUM")
        arcpy.gp.Aggregate_sa(raster,outRaster1,"120","SUM")


aggregate_rasters(r'F:\GPW\aggregate_rasters\global_tifs\gpw-v4-land-water-area')
print("finished land/water")
aggregate_rasters(r'F:\GPW\aggregate_rasters\global_tifs\gpw-v4-population-count')
print("finished counts")
aggregate_rasters(r'F:\GPW\aggregate_rasters\global_tifs\gpw-v4-population-count-adjusted-to-2015-unwpp-country-totals')
print("finished un counts")
