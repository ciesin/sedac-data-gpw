# create_gridding_folder_and_copy_tables.py
# Set up gridding geodatabase, and copy the 6 tables/feature classes needed for gridding
# Erin Doxsey-Whitfield
# 12-Aug-13

# import libraries
import os, arcpy, sys
from arcpy import env
import datetime


# set counter
startTime = datetime.datetime.now()

# define input ISO
iso = arcpy.GetParameterAsText(0)
##iso = "bvt"
print iso

# define gridding folder workspace
workspace = r'\\Dataserver0\gpw\GPW4\Gridding\country\inputs'
arcpy.env.workspace = workspace
scratch = arcpy.env.scratchFolder


# check if geodatabase already exists.  If it does exist:
newDir = workspace + os.sep + iso + ".gdb" + os.sep + iso + "_fishnet"
if arcpy.Exists(newDir):
    sys.exit("Geodatabase already exists")
    
# if it doesn't exist:
else:
    
    # create file geodatabase in scratch
    isoGDB = scratch + os.sep + iso + ".gdb"
    if arcpy.Exists(isoGDB):
        arcpy.Delete_management(isoGDB)
    else:
        pass
    arcpy.CreateFileGDB_management(scratch,iso)
    print "Created gridding file GDB in scratch"
    arcpy.AddMessage("Created gridding file GDB in scratch")

    # copy Fishnet and Water_mask feature classes to the scratch gdb
    fishnets = r'\\Dataserver0\gpw\GPW4\InputData\fishnets'
    if arcpy.Exists(fishnets + os.sep + iso + ".gdb" + os.sep + iso + "_fishnet"):
        arcpy.CopyFeatures_management(fishnets + os.sep + iso + ".gdb" + os.sep + iso + "_fishnet",isoGDB + os.sep +iso + "_fishnet")
        print "Fishnet copied"
        arcpy.AddMessage("Fishnet copied")
    else:
        print iso + " fishnet does not exist"
        arcpy.AddMessage(iso + " fishnet does not exist")
        pass
    if arcpy.Exists(fishnets + os.sep + iso + ".gdb" + os.sep + iso + "_water_mask"):
        arcpy.CopyFeatures_management(fishnets + os.sep + iso + ".gdb" + os.sep + iso + "_water_mask",isoGDB + os.sep +iso + "_water_mask")
        print "Water_mask copied"
        arcpy.AddMessage("Water_mask copied")
    else:
        print iso + " water_mask does not exist"
        arcpy.AddMessage(iso + " water_mask does not exist")
        pass

    # Input parameters
    censusTable = arcpy.GetParameterAsText(1)
    lookupTableExist = arcpy.GetParameterAsText(2)
    lookupTable = arcpy.GetParameterAsText(3)
    growthRateTable = arcpy.GetParameterAsText(4)    
    boundaryFC = arcpy.GetParameterAsText(5)
    levelNumber = arcpy.GetParameterAsText(6)

##    censusTable = r'\\Dataserver0\gpw\GPW4\Preprocessing\Country\FJI\Ingest\Census\FJI_ingest.mdb\FJI_2007_admin2_Phase1'
##    lookupTable = r'\\Dataserver0\gpw\GPW4\Preprocessing\Country\FJI\Match\FJI_match_access.mdb\fji_lookup_level2'
##    growthRateTable = r'\\Dataserver0\gpw\GPW4\GrowthRate\GLP\GLP_growth_rates.mdb\GLP_growth_rate'    
##    boundaryFC = r'\\Dataserver0\gpw\GPW4\Preprocessing\Country\FJI\Ingest\Boundary\gadm2.gdb\FJI_admin2'
##    levelNumber = "2"

    # copy tables and feature class to scratch geodatabase
    arcpy.Copy_management(censusTable,isoGDB + os.sep + os.path.basename(censusTable))
    print "Census table copied"
    arcpy.AddMessage("Census table copied")
    
    if lookupTableExist == "true":
        arcpy.Copy_management(lookupTable,isoGDB + os.sep + os.path.basename(lookupTable))
        print "Lookup table copied"
        arcpy.AddMessage("Lookup table copied")
    else:
        print "No lookup table"
        arcpy.AddMessage("No lookup table")
        pass
##    
    arcpy.Copy_management(growthRateTable,isoGDB + os.sep + os.path.basename(growthRateTable))
    print "Growth Rate table copied"
    arcpy.AddMessage("Growth Rate table copied")
    
    arcpy.CopyFeatures_management(boundaryFC,isoGDB + os.sep + iso + "_admin" + levelNumber + "_boundaries_2010")
    print "Boundaries copied"
    arcpy.AddMessage("Boundaries copied")
    
    # Copy gdb from scratch to gridding workspace
    arcpy.Copy_management(isoGDB,workspace + os.sep + iso + ".gdb")

    # Delete gdb from scratch workspace
    arcpy.Delete_management(isoGDB)
    print "Done"
    arcpy.AddMessage("Done")
    print datetime.datetime.now() - startTime    

    
##
##    # Join UBID from lookup table to census table
##    joinField = arcpy.GetParameterAsText(5)
##    arcpy.JoinField_management(censusTable,joinField,lookupTable,joinField,
    

