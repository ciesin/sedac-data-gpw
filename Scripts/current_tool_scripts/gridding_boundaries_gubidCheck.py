# Author:      Erin Doxsey-Whitfield

# This script checks that all feature classes have a GUBID

# GUBID = ISO_ubid

#-------------------------------------------------------------------------------

# Import libraries
import arcpy, os, csv
import datetime
startTime = datetime.datetime.now()

# Import workspace
workspace = r'\\Dataserver0\gpw\GPW4\Gridding\global\inputs\gridding_boundaries_working\gridding_gubid.gdb'
##workspace = r'C:\Users\edwhitfi\Desktop\scratch\gubid_test\gridding_gubid.gdb'
arcpy.env.workspace = workspace


# Overwrite pre-existing files
arcpy.env.overwriteOutput = True

# List the feature classes in the null_features.gdb
fcList = arcpy.ListFeatureClasses("*")
fcList.sort()

for fc in fcList:
    
# Parse ISO from the feature class name
        isoName = os.path.basename(fc)[0:3]
        iso = isoName.lower()
        print iso

        GUBID = "GUBID"

# Determine if field exists
        fieldList = arcpy.ListFields(fc)
        for field in fieldList:   
                if field.name == GUBID:
                        print "\tGUBID exists"
                else:
                        pass      

print "Done"


    
    
