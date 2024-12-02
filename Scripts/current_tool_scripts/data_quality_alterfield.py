# Author:      Erin Doxsey-Whitfield

# This script renames the  a field 'noData_Code_Description' field to 'NoData_Code_Comment' to each iso_null feature class
# This field will be filled in to add any relevant comments for that feature

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
        arcpy.AlterField_management(fc,"NoData_Code_Description","NoData_Code_Comment","TEXT")
        print "Renamed field"
    except:
        arcpy.GetMessages()

print "Done"


    
    
