#Jane Mills
#7/12/16
#GPW
#Divide the counts by the land area to get the densities

import arcpy, os
from arcpy import env

arcpy.CheckOutExtension("Spatial")

def calc_density(rasterFolder):
    inRoot = r'F:\GPW\aggregate_rasters\rasters_other_resolution'
    inFolder5 = os.path.join(inRoot,'0_5_degree',rasterFolder)
    inFolder25 = os.path.join(inRoot,'0_25_degree',rasterFolder)

    land5 = r'F:\GPW\aggregate_rasters\rasters_other_resolution\0_5_degree\gpw-v4-land-water-area\gpw-v4-land-water-area_land.tif'
    land25 = r'F:\GPW\aggregate_rasters\rasters_other_resolution\0_25_degree\gpw-v4-land-water-area\gpw-v4-land-water-area_land.tif'
    
    outFolder5 = inFolder5.replace('-count','-density')
    outFolder25 = inFolder25.replace('-count','-density')

    os.mkdir(outFolder5)
    os.mkdir(outFolder25)

    env.workspace = inFolder5
    rasterList5 = arcpy.ListRasters()
    for raster5 in rasterList5:
        outRaster5 = os.path.join(outFolder5,raster5.replace('count_','density_'))
        print(raster5)
        arcpy.gp.Divide_sa(raster5,land5,outRaster5)


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
