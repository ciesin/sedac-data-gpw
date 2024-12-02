import arcpy, os
from arcpy import env
from arcpy.sa import *

arcpy.env.overwriteOutput = True

arcpy.CheckOutExtension("Spatial")

arcpy.env.workspace = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Cartographic\Age_sex_test'
outputPath = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Cartographic\Age_sex_test\Output_Rasters'

# Create Rasters for the female broad age groups 0-14


# STEP 1A: Create a list and populate that list with the needed rasters
mt00_14=[]
rList = arcpy.ListRasters("*","ALL")
for r in rList:
    if "004ft" in r or "009ft" in r or "014ft" in r:
        print r
        ft00_14.append(r)

print ft00_14

# STEP 2A: Use map algebra expression to calculate the broad age group using the rasters in the list from step 1.
rasterCalc = Raster(ft00_14[0]) + Raster(ft00_14[1]) + Raster(ft00_14[2])
rasterOutput = 'gpw-v4-basic-demographic-characteristics-count-rev10-000-014ft-2010-30-sec.tif'
rasterCalc.save(os.path.join(outputPath,rasterOutput))

print "Created raster for {} {} age group".format("0 - 14","female")

###### B. CREATE A RASTER FOR THE FEMALE BROAD AGE GROUP 15 - 64 ######

# STEP 1B: Create a list and populate that list with the needed rasters
ft15_64=[]
rList = arcpy.ListRasters("*","ALL")
for r in rList:
    if "019ft" in r or "024ft" in r or "029ft" in r or "034ft" in r or "039ft" in r or "044ft" in r or "049ft" in r or "054ft" in r or "059ft" in r or "064ft" in r:
        print r
        ft15_64.append(r)

print ft15_64


###### C. CREATE A RASTER THAT COMBINES ALL FEMALE AGE GROUPS (0-65PLUS) ######

# STEP 1C: Create a list and populate that list with the needed rasters.  (Must first change the workspace since the rasters will be coming from a different folder for map algebra expression)
arcpy.env.workspace = outputPath
ft00_65plus=[]
rList2 = arcpy.ListRasters("*","ALL")
for r in rList2:
    if "065plusft" in r or "064ft" in r or "014ft" in r:
        ft00_65plus.append(r)


# STEP 2C: Use map algebra expression to calculate the broad age group using the rasters in the list from step 1.
rasterCalc2 = Raster(ft00_65plus[0]) + Raster(ft00_65plus[1]) + Raster(ft00_65plus[2])
rasterOuput2 = 'gpw-v4-basic-demographic-characteristics-count-rev10-000-065plusft-2010-30-sec.tif'
rasterCalc2.save(os.path.join(outputPath,rasterOutput2))

print "Created raster for {} {} age group".format("0 - 65 plus","female")



print "script complete" 
        

## Process rasters for 0 - 14 female age group
##ft00_14=[]
##
##rList = arcpy.ListRasters("*","ALL")
##for r in rList:
##    if "004ft" in r or "009ft" in r or "014ft" in r:
##        print r
##        ft00_14.append(r)
##
##print ft00_14
##
##firstCalc = Plus(ft00_14[0],ft00_14[1])
##print "first calculation complete"
##
##secondCalc = Plus(firstCalc, ft00_14[2])
##print "second calculation complete"
##
##calcOutput = "gpw-v4-basic-demographic-characteristics-count-rev10-000-014ft-2010-30-sec.tif"
##
##secondCalc.save(os.path.join(outputPath,calcOutput))
##

#### Process rasters for 15 - 64 female age group
##
##ft15_64 = []
##
##rList = arcpy.ListRasters("*","ALL")
##for r in rList:
##    if "019ft" in r or "024ft" in r or "029ft" in r or "034ft" in r or "039ft" in r or "044ft" in r or "049ft" in r or "054ft" in r or "059ft" in r or "064ft" in r:
##        print r
##        ft15_64.append(r)
##
##print ft15_64
##
##firstCalc = Plus(ft15_64[0],ft15_64[1])
##
##secondCalc = Plus(firstCalc, ft15_64[2])
##
##thirdCalc = Plus(secondCalc, ft15_64[3])
##
##fourthCalc = Plus(thirdCalc, ft15_64[4])
##
##fifthCalc = Plus(fourthCalc, ft15_64[5])
##
##sixthCalc = Plus(fifthCalc, ft15_64[6])
##
##seventhCalc = Plus(sixthCalc, ft15_64[7])
##
##eigthCalc = Plus(seventhCalc, ft15_64[8])
##
##ninthCalc = Plus(eigthCalc, ft15_64[9])
##
##
##calcOutput = "gpw-v4-basic-demographic-characteristics-count-rev10-015-064ft-2010-30-sec.tif"
##
##ninthCalc.save(os.path.join(outputPath,calcOutput))
##
##
#### Process rastesr for 15 - 49 female age group
##
##ft15_49 = []
##
##rList = arcpy.ListRasters("*","ALL")
##for r in rList:
##     if "019ft" in r or "024ft" in r or "029ft" in r or "034ft" in r or "039ft" in r or "044ft" in r or "049ft" in r:
##        print r
##        ft15_49.append(r)
##
##firstCalc = Plus(ft15_49[0],ft15_49[1])
##
##secondCalc = Plus(firstCalc, ft15_49[2])
##
##thirdCalc = Plus(secondCalc, ft15_49[3])
##
##fourthCalc = Plus(thirdCalc, ft15_49[4])
##
##fifthCalc = Plus(fourthCalc, ft15_49[5])
##
##sixthCalc = Plus(fifthCalc, ft15_49[6])
##
##
##calcOutput = "gpw-v4-basic-demographic-characteristics-count-rev10-015-049ft-2010-30-sec.tif"
##
##sixthCalc.save(os.path.join(outputPath,calcOutput))
##




## processing raster to combine all age groups
arcpy.env.workspace = outputPath

ft00_65plus=[]

rList = arcpy.ListRasters("*","ALL")
for r in rList:
    if "065plusft" in r:
        ft00_65plus.append(r)
        

rList2 = arcpy.ListRasters("*","ALL")
for r in rList2:
    if "064ft" in r or "014ft" in r:
        ft00_65plus.append(r)

firstCalc = Plus(ft00_65plus[0],ft00_65plus[1])
secondCalc = Plus(firstCalc,ft00_65plus[2])

secondCalc.save("gpw-v4-basic-demographic-characteristics-count-rev10-000-065plusft-2010-30-sec.tif")




print "script complete"


                


