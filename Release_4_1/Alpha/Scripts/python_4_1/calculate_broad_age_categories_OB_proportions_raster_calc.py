#Calculate broad age groups proportions

import arcpy, os
from arcpy import env
from arcpy.sa import *

arcpy.env.overwriteOutput = True

arcpy.CheckOutExtension("Spatial")

arcpy.env.workspace = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Cartographic\Age_sex_test\Output_Rasters'
outputPath = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Cartographic\Age_sex_test\Output_Rasters'
FemaleTotal = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Cartographic\Age_sex_test\Output_Rasters\gpw-v4-basic-demographic-characteristics-count-rev10-000-065plusft-2010-30-sec.tif'
MaleTotal = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Cartographic\Age_sex_test\Output_Rasters\gpw-v4-basic-demographic-characteristics-count-rev10-000-065plusmt-2010-30-sec.tif'


# STEP 1A: Create a female list and populate that list with the needed rasters
ftRasters=[]
rList = arcpy.ListRasters("*","ALL")
for r in rList:
    if "004ft" in r or "014ft" in r or "-rev10-065plusft-" in r or "049ft" in r or "064ft" in r:
        print r
        ftRasters.append(r)

for raster in ftRasters:
    rasterCalc = Raster(raster)/Raster(FemaleTotal)
    rasterCalc.save(os.path.join(outputPath, raster[:-4]+ "_P.tif"))

print "Female Proportions Complete"

# STEP 1B: Create a male list and populate that list with the needed rasters

mtRasters=[]
rList2 = arcpy.ListRasters("*","ALL")
for r in rList2:
    if "004mt" in r or "014mt" in r or "-rev10-065plusmt-"  in r or "064mt" in r:
        print r
        mtRasters.append(r)

for raster in mtRasters:
    rasterCalc2 = Raster(raster)/Raster(MaleTotal)
    rasterCalc2.save(os.path.join(outputPath, raster[:-4] + "_P.tif"))

print "Male Proportions Complete"




                


