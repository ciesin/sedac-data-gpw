#Jane Mills
#7/12/16
#GPW
#Validate the grids

import arcpy, os
from arcpy import env

arcpy.CheckOutExtension("Spatial")

def convert_ascii(resolution):
    inRoot = r'F:\GPW\aggregate_rasters'
    inFolder = os.path.join(inRoot,'rasters_other_resolution',resolution)
    outFolder = os.path.join(inRoot,'ascii',resolution)

    fList = os.listdir(inFolder)

    for f in fList:
        fpath = os.path.join(inFolder,f)
        env.workspace = fpath
        outf = os.path.join(outFolder,f)
        os.mkdir(outf)

        rList = arcpy.ListRasters()
        for raster in rList:
            print(raster)
            outAscii = os.path.join(outf,raster[:-4]+'.txt')
            arcpy.RasterToASCII_conversion(raster,outAscii)


convert_ascii('0_25_degree')
print("finished 0.25 degree")

convert_ascii('0_5_degree')
print("finished 0.5 degree")

convert_ascii('1_degree')
print("finished 1 degree")

convert_ascii('2_5_minute')
print("finished 2.5 minute")
