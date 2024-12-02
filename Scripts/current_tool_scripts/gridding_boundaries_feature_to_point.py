# Author:      Erin Doxsey-Whitfield

# This script converts polygons to points

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

# Use to skip countries that or cause problems (will do those manually)
##        if iso.startswith(('vat'))== False:

        out_feature_gdb = r'\\Dataserver0\gpw\GPW4\Gridding\global\inputs\gridding_boundaries_working\gridding_centroids.gdb'
        out_feature_class = out_feature_gdb + os.sep + iso + "_centroids"

# for each country, convert features to point (centroids)               
        arcpy.FeatureToPoint_management(fc, out_feature_class, "INSIDE")
        print "\tCentroids created"
        

##        else:
##            print "\t" + iso + " skipped"
    
print "Done"


    
    
