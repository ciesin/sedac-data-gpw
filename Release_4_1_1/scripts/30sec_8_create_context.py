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

newPop = r'F:\gpw\v411\rasters_30sec_fixed_zeros\gpw_v4_population_count_rev11_2010_30_sec.tif'
popFilled = os.path.join(outFolder,'pop_remove_noData.tif')
outCon = Con(IsNull(Raster(newPop)) == 1, -1, Raster(newPop))
arcpy.CopyRaster_management(outCon, popFilled)

popDiff = os.path.join(outFolder,"pop_diff_2010.tif")
#outCon = Con((IsNull(Raster(pop2010))==0) & (IsNull(Raster(male))==1) & (IsNull(Raster(female))==1), 1, 0)
#arcpy.CopyRaster_management(outCon, popDiff)

outReclass = os.path.join(outFolder,'Reclass_data_context_zeros.tif')
arcpy.gp.Reclassify_sa(context, "Value", "0 0;201 201;202 202;203 203;204 204;205 205;206 206;207 0;NODATA 0", outReclass, "DATA")

popClass2 = os.path.join(outFolder,"pop_classification_2010_null_ocean.tif")
conFilled = os.path.join(outFolder,"Reclass_data_context_zeros_mask_pop.tif")
conContext = Con(Raster(popClass2) == 1, 0, Raster(outReclass))
arcpy.CopyRaster_management(conContext, conFilled)

zeroContext = os.path.join(outFolder,'Reclass_data_context_zeros_mask_pop_205.tif')
conContext = Con((Raster(popFilled) == 0) & (Raster(conFilled) == 0), 205, Raster(conFilled))
arcpy.CopyRaster_management(conContext, zeroContext)

finalContext = os.path.join(outFolder,"gpw_v4_data_quality_indicators_rev11_context_30_sec.tif")
conContext = Con((Raster(zeroContext) == 0) & (Raster(popDiff) == 1), 207, Raster(zeroContext))
arcpy.CopyRaster_management(conContext, finalContext)

arcpy.AddField_management(finalContext,"CATEGORY","TEXT","","","75")
with arcpy.da.UpdateCursor(finalContext,["VALUE","CATEGORY"]) as cursor:
    for row in cursor:
        if row[0] == 0: row[1] = "Not applicable"
        if row[0] == 201: row[1] = "Park or protected area"
        if row[0] == 202: row[1] = "Military district, airport zone, or other infrastructure"
        if row[0] == 203: row[1] = "Not enumerated or not reported in census"
        if row[0] == 204: row[1] = "No households"
        if row[0] == 205: row[1] = "Uninhabited"
        if row[0] == 206: row[1] = "Population not gridded"
        if row[0] == 207: row[1] = "Missing age and/or sex data"
        cursor.updateRow(row)




