#Jane Mills
#6/28/2017
#GPW
#stack rasters into netCDF

import arcpy, os
from arcpy import env

inFolder = r'D:\gpw\release_4_1\low_res'
resolutions = ['2pt5_min','15_min','30_min','1_deg']
scales = ['5','30','60','120']

env.workspace = inFolder

for res in resolutions:
    print res
    rasterList = arcpy.ListRasters("*"+res+"*")
    rasterList.sort()

    for raster in rasterList:
        outFile = r'testnetcdf2.nc'
        arcpy.md.RasterToNetCDF(raster,outFile,raster,None,"lon","lat",None,None)

