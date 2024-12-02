## Olena
## 5/4/2017
## This script creates broad age group categories for males.  


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


###### A. CREATE A RASTER FOR THE MALE BROAD AGE GROUP 0 - 14 ######


# STEP 1A: Create a list and populate that list with the needed rasters
mt00_14=[]
rList = arcpy.ListRasters("*","ALL")
for r in rList:
    if "004mt" in r or "009mt" in r or "014mt" in r:
        print r
        mt00_14.append(r)

print mt00_14



# STEP 2A: Use map algebra expression to calculate the broad age group using the rasters in the list from step 1.
rasterCalc = Raster(mt00_14[0]) + Raster(mt00_14[1]) + Raster(mt00_14[2])
rasterOutput = 'gpw-v4-basic-demographic-characteristics-count-rev10-000-014mt-2010-30-sec.tif'
rasterCalc.save(os.path.join(outputPath,rasterOutput))

print "Created raster for {} {} age group".format("0 - 14","male")


###### B. CREATE A RASTER FOR THE MALE BROAD AGE GROUP 15 - 64 ######

# STEP 1B: Create a list and populate that list with the needed rasters
mt15_64=[]
rList = arcpy.ListRasters("*","ALL")
for r in rList:
    if "019mt" in r or "024mt" in r or "029mt" in r or "034mt" in r or "039mt" in r or "044mt" in r or "049mt" in r or "054mt" in r or "059mt" in r or "064mt" in r:
        print r
        mt15_64.append(r)

print mt15_64

# STEP 2B: Use map algebra expression to calculate the broad age group using the rasters in the list from step 1.
rasterCalc = Raster(mt15_64[0]) + Raster(mt15_64[1]) + Raster(mt15_64[2]) + Raster(mt15_64[3]) + Raster(mt15_64[4]) + Raster(mt15_64[5]) + Raster(mt15_64[6])
rasterOutput = 'gpw-v4-basic-demographic-characteristics-count-rev10-015-064mt-2010-30-sec.tif'
rasterCalc.save(os.path.join(outputPath,rasterOutput))

print "Created raster for {} {} age group".format("15 - 64","male")


###### C. CREATE A RASTER THAT COMBINES ALL MALE AGE GROUPS (0-65PLUS) ######

# STEP 1C: Create a list and populate that list with the needed rasters.  (Must first change the workspace since the rasters will be coming from a different folder for map algebra expression)
arcpy.env.workspace = outputPath
mt00_65plus=[]
rList2 = arcpy.ListRasters("*","ALL")
for r in rList2:
    if "065plusmt" in r or "064mt" in r or "014mt" in r:
        mt00_65plus.append(r)


# STEP 2C: Use map algebra expression to calculate the broad age group using the rasters in the list from step 1.
rasterCalc2 = Raster(mt00_65plus[0]) + Raster(mt00_65plus[1]) + Raster(mt00_65plus[2])
rasterOutput2 = 'gpw-v4-basic-demographic-characteristics-count-rev10-000-065plusmt-2010-30-sec.tif'
rasterCalc2.save(os.path.join(outputPath,rasterOutput2))

print "Created raster for {} {} age group".format("0 - 65 plus","male")



print "script complete" 












                     
