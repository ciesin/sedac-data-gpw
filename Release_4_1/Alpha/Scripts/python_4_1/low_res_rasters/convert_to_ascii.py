#Jane Mills
#7/12/16
#GPW
#Validate the grids

import arcpy, os
from arcpy import env

arcpy.CheckOutExtension("Spatial")

#root = r'D:\gpw\release_4_1\gdal_tifs'
#outFolder = r'D:\gpw\release_4_1\ascii'
root = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\rasters\gdal_tifs'
outFolder = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\netCDF\rasters'

rectangles = ["-180 0 -90 90","-90 0 0 90","0 0 90 90","90 0 180 90",
              "-180 -90 -90 -0.000001","-90 -90 0 -0.000001","0 -90 90 -0.000001","90 -90 180 -0.000001"]

env.workspace = root
rList = arcpy.ListRasters("*e_a0*bt*cntm_30_sec.tif")
rList.sort()

for r in rList:
    print r
    i = 0
    rect = rectangles[i]
    outTemp = os.path.join(outFolder,os.path.basename(r)[:-4]+'_'+str(i+1)+'.tif')
    arcpy.Clip_management(r, rect, outTemp)



##for r in rList:
##    print r
##    if '30_sec' in r:
##        for i in range(len(rectangles)):
##            outAscii = os.path.join(outFolder,r[:-4]+'_'+str(i+1)+'.txt')
##            rect = rectangles[i]
##            outTemp = os.path.join(outFolder,'temp',r+'_'+str(i+1)+'.tif')
##            arcpy.Clip_management(r, rect, outTemp)
##            arcpy.RasterToASCII_conversion(outTemp,outAscii)
##            #arcpy.Delete_management(outTemp)
##
##    else:
##        outAscii = os.path.join(outFolder,r[:-4]+'.txt')
##        arcpy.RasterToASCII_conversion(r,outAscii)


print "complete!"


