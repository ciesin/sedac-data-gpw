#Jane Mills
#7/13/16
#GPW
#Validate the grids

import arcpy, os
from arcpy import env

arcpy.CheckOutExtension("Spatial")

def validate(resolution):
    inRoot = r'F:\GPW\aggregate_rasters\rasters_other_resolution'
    inFolder = os.path.join(inRoot,resolution)

    fList = os.listdir(inFolder)
    fList.sort()

    outGDB = os.path.join(inFolder,'validation.gdb')
    arcpy.CreateFileGDB_management(inFolder,'validation.gdb')

    idGrid = os.path.join(inFolder,'gpw-v4-national-identifier-grid','gpw-v4-national-identifier-grid.tif')

    for f in fList:
        if f == 'gpw-v4-national-identifier-grid' or f == 'gpw-v4-land-water-area':
            pass
        else:
            env.workspace = os.path.join(inFolder,f)
            rasterList = arcpy.ListRasters()
            
            for raster in rasterList:
                print(raster)
                outTable = os.path.join(outGDB,'stats_'+raster[7:-4].replace('-','_'))
                arcpy.gp.ZonalStatisticsAsTable_sa(idGrid,"Value",raster,outTable,"DATA","ALL")


validate('0_25_degree')
print("finished 0.25 degree")

validate('0_5_degree')
print("finished 0.5 degree")

validate('1_degree')
print("finished 1 degree")

validate('2_5_minute')
print("finished 2.5 minute")
