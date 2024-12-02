#Jane Mills
#7/12/16
#GPW
#Convert the data quality layers to ascii

import arcpy, os
from arcpy import env

arcpy.CheckOutExtension("Spatial")

def convert_ascii(resolution):
    inRoot = r'F:\GPW\aggregate_rasters'
    inFolder = os.path.join(inRoot,'rasters_other_resolution',resolution,'gpw-v4-data-quality-indicators')
    outFolder = os.path.join(inRoot,'ascii',resolution,'gpw-v4-data-quality-indicators')

    os.mkdir(outFolder)

    maua = 'gpw-v4-data-quality-indicators_mean-administrative-unit-area.tif'
    dq = 'gpw-v4-data-quality-indicators_data-context.tif'

    raster1 = os.path.join(inFolder,maua)
    raster2 = os.path.join(inFolder,dq)

    outAscii1 = os.path.join(outFolder,maua[:-4]+'.txt')
    outAscii2 = os.path.join(outFolder,dq[:-4]+'.txt')
    
    arcpy.RasterToASCII_conversion(raster1,outAscii1)
    arcpy.RasterToASCII_conversion(raster2,outAscii2)


convert_ascii('0_25_degree')
print("finished 0.25 degree")

convert_ascii('0_5_degree')
print("finished 0.5 degree")

convert_ascii('1_degree')
print("finished 1 degree")

convert_ascii('2_5_minute')
print("finished 2.5 minute")
