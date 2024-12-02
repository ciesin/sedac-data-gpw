# Author:      Erin Doxsey-Whitfield

# This script adds a field 'noData_Code' to each iso_null feature class
# This field will be filled in to categorize each of the nodata features

#-------------------------------------------------------------------------------

# Import libraries
import arcpy, os, csv
import datetime
startTime = datetime.datetime.now()

# Import workspace
workspace = r'\\Dataserver0\gpw\GPW4\Gridding\global\data_quality\null_features\null_features.gdb'
arcpy.env.workspace = workspace

# Overwrite pre-existing files
arcpy.env.overwriteOutput = True

# List the feature classes in the null_features.gdb
fcList = arcpy.ListFeatureClasses("*")
fcList.sort()



# Add NoData_Code field to each fc
for fc in fcList:
    try:
        print fc
        arcpy.AddField_management(fc,"NoData_Code_Description","TEXT")
        print "Added field"
    except:
        arcpy.GetMessages()

print "Done"


    
    
