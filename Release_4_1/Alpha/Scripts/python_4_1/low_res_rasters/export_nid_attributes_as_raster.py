#Jane Mills
#GPW
#Aggregate the national identifier grid

import arcpy, os
from arcpy import env
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")

inGDB = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\national_identifier_edits\national_identifier_polygons.gdb'
extents = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\ancillary\extents'
outF = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\netCDF\quality_tifs'

env.workspace = inGDB
fcList = arcpy.ListFeatureClasses()
fcList.sort()

fieldList = ['DATACODE','DATAYEAR','DATALEVEL','GRSTART','GREND','GRLEVEL','LASTCENSUS']
nameList = ['data_code','data_year','data_level','gr_start','gr_end','gr_level','last_census']

for fc in fcList:
    print fc
    res = fc[32:]
    extRast = os.path.join(extents,'gpw4_extent_'+res+'.tif')

    env.snapRaster = extRast
    extRaster = arcpy.sa.Raster(extRast)
    env.extent = extRaster.extent
    env.cellSize = extRast

    for i in range(len(fieldList)):
        field = fieldList[i]
        print field
        
        outName = 'gpw_v4_' + nameList[i] + '_' + res + '.tif'
        outR = os.path.join(outF,outName)

        arcpy.PolygonToRaster_conversion(fc,field,outR,"CELL_CENTER","NONE")


print "complete"
