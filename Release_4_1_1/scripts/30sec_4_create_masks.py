# -*- coding: utf-8 -*-
"""
Created on Fri Oct 19 14:35:41 2018

@author: jmills
"""

import arcpy, os
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True

arcpy.env.scratchWorkspace = r'F:\gpw\v411\scratch'
mask = Raster(r'F:\gpw\v411\ancillary\water_classification.tif')
arcpy.env.extent = arcpy.Describe(mask).Extent

outFolder = r'F:\gpw\v411\masks'
pop2010 = r'\\Dataserver1\gpw\GPW4\Release_4_1\Alpha\Gridding\rasters\gpw_v4_population_count_rev10_2015_30_sec.tif'
context = r'\\Dataserver1\gpw\GPW4\Release_4_1\Alpha\Gridding\rasters\gpw_v4_data_quality_indicators_rev10_context_30_sec.tif'
natid = r'F:\gpw\v411\rasters_30sec_fixed_zeros\gpw_v4_national_identifier_grid_rev11_30_sec.tif'
male = r'\\Dataserver1\gpw\GPW4\Release_4_1\Alpha\Gridding\rasters\gpw_v4_basic_demographic_characteristics_rev10_atotpopmt_2010_cntm_30_sec.tif'
female = r'\\Dataserver1\gpw\GPW4\Release_4_1\Alpha\Gridding\rasters\gpw_v4_basic_demographic_characteristics_rev10_atotpopft_2010_cntm_30_sec.tif'

popClass = os.path.join(outFolder,"pop_classification_2010.tif")
outCon = Con(IsNull(pop2010) == 1, -1, 1)
arcpy.CopyRaster_management(outCon, popClass)

popClass2 = os.path.join(outFolder,"pop_classification_2010_null_ocean.tif")
outCon = Con(Raster(natid) > 0, Raster(popClass))
arcpy.CopyRaster_management(outCon, popClass2)

conFilled = os.path.join(outFolder,"data_context_reclass.tif")
conContext = Con(IsNull(Raster(context)) == 1, 0, Con((Raster(context) == 201) | (Raster(context) == 202) | (Raster(context) == 203) | (Raster(context) == 206), 1, 2))
arcpy.CopyRaster_management(conContext, conFilled)

popClass3 = os.path.join(outFolder,"pop_mask.tif")
outCon = Con((Raster(popClass2) == -1) & (Raster(conFilled) != 1), 0, Raster(popClass2))
arcpy.CopyRaster_management(outCon, popClass3)

popDiff = os.path.join(outFolder,"pop_diff_2010.tif")
outCon = Con((IsNull(Raster(pop2010))==0) & (IsNull(Raster(male))==1) & (IsNull(Raster(female))==1), 1, 0)
arcpy.CopyRaster_management(outCon, popDiff)

demoClass = os.path.join(outFolder,"demographic_mask.tif")
outCon = Con((Raster(popClass3) == 1) & (Raster(popDiff) == 1), -1, Raster(popClass3))
arcpy.CopyRaster_management(outCon, demoClass)







