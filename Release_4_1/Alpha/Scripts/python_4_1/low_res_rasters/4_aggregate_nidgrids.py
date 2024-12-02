#Jane Mills
#GPW
#Aggregate the national identifier grid

import arcpy, os
from arcpy import env
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")

inR = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\rasters\gdal_tifs\gpw_v4_national_identifier_30_sec.tif'
outF = r'D:\gpw\release_4_1\low_res'
resolutions = ['2pt5_min','15_min','30_min','1_deg']
scales = ['5','30','60','120']

gridDict = {}
with arcpy.da.SearchCursor(inR,["VALUE","ISOCODE","UNSDCODE","NAME0","CIESINCODE"]) as cursor:
    for row in cursor:
        gridDict[row[0]] = row[1:]

for i in range(4):
    res = resolutions[i]
    print res
    scale = scales[i]
    ext = os.path.join(outF,'extents','gpw4_extent_'+res+'.tif')
    extRast = arcpy.sa.Raster(ext)
    env.snapRaster = ext
    env.extent = extRast.extent

    outR = os.path.join(outF,'gpw_v4_national_identifier_'+res+'_temp.tif')
    outRName = 'gpw_v4_national_identifier_'+res+'_temp.tif'
    finalR = os.path.join(outF,'gpw_v4_national_identifier_'+res+'.tif')

    arcpy.gp.BlockStatistics_sa(inR,outR,"Rectangle "+scale+" "+scale+" CELL", "MAJORITY", "DATA")
    arcpy.gp.Aggregate_sa(outR,finalR,scale, "MEDIAN", "EXPAND", "DATA")

    arcpy.AddField_management(finalR,"ISOCODE","TEXT","","","5")
    arcpy.AddField_management(finalR,"UNSDCODE","SHORT","5")
    arcpy.AddField_management(finalR,"NAME0","TEXT","","","100")
    arcpy.AddField_management(finalR,"CIESINCODE","SHORT","5")

    with arcpy.da.UpdateCursor(finalR,["VALUE","ISOCODE","UNSDCODE","NAME0","CIESINCODE"]) as cursor:
        for row in cursor:
            if row[0] in gridDict:
                row[1:] = gridDict[row[0]]
                cursor.updateRow(row)
            else:
                print "found an error"


