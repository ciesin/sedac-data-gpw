#Jane Mills
#7/12/16
#GPW
#Divide the counts by the land area to get the densities

import arcpy, os
from arcpy import env

arcpy.CheckOutExtension("Spatial")

def calc_density(rasterFolder):
    inRoot = r'F:\GPW\aggregate_rasters\rasters_other_resolution'
    inFolder1 = os.path.join(inRoot,'1_degree',rasterFolder)
    inFolder25 = os.path.join(inRoot,'2_5_minute',rasterFolder)

    land1 = r'F:\GPW\aggregate_rasters\rasters_other_resolution\1_degree\gpw-v4-land-water-area\gpw-v4-land-water-area_land.tif'
    land25 = r'F:\GPW\aggregate_rasters\rasters_other_resolution\2_5_minute\gpw-v4-land-water-area\gpw-v4-land-water-area_land.tif'
    
    outFolder1 = inFolder1.replace('-count-','-density-')
    outFolder25 = inFolder25.replace('-count-','-density-')

    os.mkdir(outFolder1)
    os.mkdir(outFolder25)

    env.workspace = inFolder1
    rasterList1 = arcpy.ListRasters()
    for raster1 in rasterList1:
        outRaster1 = os.path.join(outFolder1,raster1.replace('count_','density_'))
        print(raster1)
        arcpy.gp.Divide_sa(raster1,land1,outRaster1)
        

    env.workspace = inFolder25
    rasterList25 = arcpy.ListRasters()
    for raster25 in rasterList25:
        outRaster25 = os.path.join(outFolder25,raster25.replace('count_','density_'))
        print(raster25)
        arcpy.gp.Divide_sa(raster25,land25,outRaster25)

calc_density('gpw-v4-population-count')
print("finished counts")
calc_density('gpw-v4-population-count-adjusted-to-2015-unwpp-country-totals')
print("finished un counts")
