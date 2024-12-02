# -*- coding: utf-8 -*-
"""
Created on Fri Oct 19 14:35:41 2018

@author: jmills
"""

import arcpy, os
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")

arcpy.env.scratchWorkspace = r'F:\gpw\v411\scratch'
arcpy.env.compression = "LZW"
arcpy.env.overwriteOutput = True

root = r'F:\gpw\v411\ancillary'
totalArea = r'F:\gpw\v411\ancillary\pixelarea.tif'
waterMask = r'F:\gpw\v411\rasters_30sec_fixed_zeros\gpw_v4_data_quality_indicators_rev11_watermask_30_sec.tif'
oldWaterMask = r'F:\gpw\v411\scratch\gpw_v4_watermask.tif'
land = r'F:\gpw\v411\rasters_30sec_fixed_zeros\gpw_v4_land_water_area_rev11_landareakm_30_sec.tif'
water = r'\\Dataserver1\gpw\GPW4\Release_4_1\Alpha\Gridding\rasters\gpw_v4_land_water_area_rev10_waterareakm_30_sec.tif'

arcpy.env.Extent = arcpy.Describe(totalArea).Extent

waterFilled = os.path.join(root,'waterarea_filled.tif')
outCon = Con((IsNull(Raster(water)) == 1) & (Raster(waterMask) != 3), 0, Raster(water))
arcpy.CopyRaster_management(outCon, waterFilled)

#Pixels that have flipped from null to partial water - subtract land area from total area to get water area
outRast = os.path.join(root,'gpw_v4_land_water_area_rev11_waterareakm_30_sec.tif')
outCon = Con((Raster(waterMask) == 1) & (IsNull(Raster(oldWaterMask)) == 1), Raster(totalArea)-Raster(land),Raster(waterFilled))
arcpy.CopyRaster_management(outCon, outRast)


