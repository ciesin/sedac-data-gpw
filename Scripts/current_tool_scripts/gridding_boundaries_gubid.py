# Author:      Erin Doxsey-Whitfield

# This script creates a ISO_GPW4 field and a GUBID (Global UBID) from the UBID

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
        if iso.startswith(('vcs'))== True:

# Add ISO_GPW4 field to each fc
            arcpy.AddField_management(fc,"ISO_GPW4","TEXT")
            print "\tAdded ISO_GPW4 field"
        
    # Calculate ISO_GPW4 field
            arcpy.CalculateField_management(fc,"ISO_GPW4","'" + iso +"'","PYTHON")
            print "\tCalculated ISO_GPW4"      

    # Add GUBID field to each fc
            arcpy.AddField_management(fc,"GUBID","TEXT")
            print "\tAdded GUBID field"

        
    # Calculate GUBID from ISO and string of UBID
            arcpy.CalculateField_management(fc,"GUBID", "!ISO_GPW4!+'_'+str(!UBID!)","PYTHON")
            print "\tCalculated GUBID"

        else:
            print iso + " skipped"
    
print "Done"


    
    
