#Jane Mills
#GPW
#Make age/sex rasters

import arcpy, os
from arcpy import env
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")

env.overwriteOutput = True
env.scratchWorkspace = r'F:\gpw\v411\scratch'
env.compression = "LZW"

inFolder = r'\\Dataserver1\gpw\GPW4\Release_411\data\rasters_30sec'
outFolder = r'F:\gpw\v411\mxds_data'

totalPop = os.path.join(inFolder,'gpw_v4_population_count_rev11_2010_30_sec.tif')
male = os.path.join(inFolder,'gpw_v4_basic_demographic_characteristics_rev11_atotpopmt_2010_cntm_30_sec.tif')
female = os.path.join(inFolder,'gpw_v4_basic_demographic_characteristics_rev11_atotpopft_2010_cntm_30_sec.tif')

child = os.path.join(inFolder,'gpw_v4_basic_demographic_characteristics_rev11_a000_014bt_2010_cntm_30_sec.tif')
working = os.path.join(inFolder,'gpw_v4_basic_demographic_characteristics_rev11_a015_064bt_2010_cntm_30_sec.tif')
elderly = os.path.join(inFolder,'gpw_v4_basic_demographic_characteristics_rev11_a065plusbt_2010_cntm_30_sec.tif')

womchild = os.path.join(inFolder,'gpw_v4_basic_demographic_characteristics_rev11_a015_049ft_2010_cntm_30_sec.tif')

#Children %
outChild = os.path.join(outFolder,'children_percent.tif')
outCon = Con(Raster(totalPop) == 0, 0, 100*Raster(child)/Raster(totalPop))
arcpy.CopyRaster_management(outCon,outChild)

#Elderly %
outElderly = os.path.join(outFolder,'elderly_percent.tif')
outCon = Con(Raster(totalPop) == 0, 0, 100*Raster(elderly)/Raster(totalPop))
arcpy.CopyRaster_management(outCon,outElderly)

#Sex Ratio (males per 100 females)
outSex = os.path.join(outFolder,'sex_ratio.tif')
outCon = Con(Raster(female) > 0, 100*Raster(male)/Raster(female))
arcpy.CopyRaster_management(outCon,outSex)

#Dependency
outDep = os.path.join(outFolder,'dependency_ratio.tif')
outCon = Con(Raster(working) > 0, 100*(Raster(child) + Raster(elderly))/Raster(working))
arcpy.CopyRaster_management(outCon,outDep)

#Woman of Childbearing age %
outWomChild = os.path.join(outFolder,'woman_childbearing_percent.tif')
outCon = Con(Raster(totalPop) == 0, 0, 100*Raster(womchild)/Raster(totalPop))
arcpy.CopyRaster_management(outCon,outWomChild)




