## Olena
## 5/4/2017
## This script creates broad age group categories for totals.  


## Import all needed modules
import arcpy, os
from arcpy import env
from arcpy.sa import *

## Set up all other components
arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension("Spatial")


## Set folder paths and workspaces
arcpy.env.workspace = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Cartographic\Age_sex_test'
outputPath = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Cartographic\Age_sex_test\Output_Rasters'


###### A. CREATE A RASTER FOR THE TOTAL BROAD AGE GROUP 0 - 14 ######


# STEP 1A: Create a list and populate that list with the needed rasters
bt00_14=[]
rList = arcpy.ListRasters("*","ALL")
for r in rList:
    if "004bt" in r or "009bt" in r or "014bt" in r:
        print r
        mt00_14.append(r)

print bt00_14



# STEP 2A: Use map algebra expression to calculate the broad age group using the rasters in the list from step 1.
rasterCalc = Raster(bt00_14[0]) + Raster(bt00_14[1]) + Raster(bt00_14[2])
rasterOutput = 'gpw-v4-basic-demographic-characteristics-count-rev10-000-014bt-2010-30-sec.tif'
rasterCalc.save(os.path.join(outputPath,rasterOutput))

print "Created raster for {} {} age group".format("0 - 14","total")


###### B. CREATE A RASTER FOR THE TOTAL BROAD AGE GROUP 15 - 64 ######

# STEP 1B: Create a list and populate that list with the needed rasters
bt15_64=[]
rList = arcpy.ListRasters("*","ALL")
for r in rList:
    if "019bt" in r or "024bt" in r or "029bt" in r or "034bt" in r or "039bt" in r or "044bt" in r or "049bt" in r or "054bt" in r or "059bt" in r or "064bt" in r:
        print r
        bt15_64.append(r)

print bt15_64

# STEP 2B: Use map algebra expression to calculate the broad age group using the rasters in the list from step 1.
rasterCalc = Raster(bt15_64[0]) + Raster(bt15_64[1]) + Raster(bt15_64[2]) + Raster(bt15_64[3]) + Raster(bt15_64[4]) + Raster(bt15_64[5]) + Raster(bt15_64[6])
rasterOutput = 'gpw-v4-basic-demographic-characteristics-count-rev10-015-064mt-2010-30-sec.tif'
rasterCalc.save(os.path.join(outputPath,rasterOutput))

print "Created raster for {} {} age group".format("15 - 64","total")


###### C. CREATE A RASTER THAT COMBINES ALL TOTAL AGE GROUPS (0-65PLUS) ######

# STEP 1C: Create a list and populate that list with the needed rasters.  (Must first change the workspace since the rasters will be coming from a different folder for map algebra expression)
arcpy.env.workspace = outputPath
bt00_65plus=[]
rList2 = arcpy.ListRasters("*","ALL")
for r in rList2:
    if "065plusbt" in r or "064bt" in r or "014bt" in r:
        bt00_65plus.append(r)


# STEP 2C: Use map algebra expression to calculate the broad age group using the rasters in the list from step 1.
rasterCalc2 = Raster(bt00_65plus[0]) + Raster(bt00_65plus[1]) + Raster(bt00_65plus[2])
rasterOutput2 = 'gpw-v4-basic-demographic-characteristics-count-rev10-000-065plusbt-2010-30-sec.tif'
rasterCalc2.save(os.path.join(outputPath,rasterOutput2))

print "Created raster for {} {} age group".format("0 - 65 plus","total")



print "script complete" 
