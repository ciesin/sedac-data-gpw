# -*- coding: utf-8 -*-
"""
Created on Mon Oct 22 11:10:29 2018

@author: jmills
"""

import arcpy

root = r'F:\gpw\v411\rasters_30sec_fixed_zeros'
root = r'F:\gpw\v411\rasters_lower_resolution'
root = r'\\Dataserver1\gpw\GPW4\Release_411\netCDF\quality_tifs'

fullRast = r'F:\gpw\v411\ancillary\water_classification.tif'
fullExt = arcpy.Describe(fullRast).Extent
ext = [round(fullExt.XMin,1), round(fullExt.XMax,1), round(fullExt.YMin,1), round(fullExt.YMax,1)]

arcpy.env.workspace = root

rList = arcpy.ListRasters()
rList.sort()

for r in rList:
    fullExt = arcpy.Describe(fullRast).Extent
    rastExt = [round(fullExt.XMin,1), round(fullExt.XMax,1), round(fullExt.YMin,1), round(fullExt.YMax,1)]

    if not rastExt == ext:
        print(r + ": " + rastExt)

