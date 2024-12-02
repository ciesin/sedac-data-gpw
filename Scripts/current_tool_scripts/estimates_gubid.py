# Author:      Erin Doxsey-Whitfield

# This script creates a ISO_GPW4 field and a GUBID (Global UBID) and GUSCID (Global USCID) from the UBID and USCID

# GUBID = ISO_ubid; GUSCID = ISO_uscid

#-------------------------------------------------------------------------------

# Import libraries
import arcpy, os, csv
import datetime
startTime = datetime.datetime.now()

# Import workspace
workspace = r'C:\Users\edwhitfi\Desktop\GPW4\inputs\estimates_tables_gubid.gdb'
##workspace = r'C:\Users\edwhitfi\Desktop\scratch\gubid_test\estimates_table_gubid_guscid.gdb'
arcpy.env.workspace = workspace


# Overwrite pre-existing files
arcpy.env.overwriteOutput = True

# List the feature classes in the null_features.gdb
tableList = arcpy.ListTables("*")
tableList.sort()

for table in tableList:
    
# Parse ISO from the feature class name
        isoName = os.path.basename(table)[0:3]
        iso = isoName.lower()
        print iso

# Use to skip countries that or cause problems (will do those manually)
        if iso.startswith(('a','b','alb','and','arg','bdi','ben','bol','btn','che','dza','fro','glp','isl','lka','mac'))== False:

    # Add ISO_GPW4 field to each fc
            arcpy.AddField_management(table,"ISO_GPW4","TEXT")
            print "\tAdded ISO_GPW4 field"
        
    # Calculate ISO_GPW4 field
            arcpy.CalculateField_management(table,"ISO_GPW4","'" + iso +"'","PYTHON")
            print "\tCalculated ISO_GPW4"      

    # Add GUBID field to each fc
            arcpy.AddField_management(table,"GUBID","TEXT")
            print "\tAdded GUBID field"
            
    # Calculate GUBID from ISO and string of UBID
            arcpy.CalculateField_management(table,"GUBID", "!ISO_GPW4!+'_'+str(!UBID!)","PYTHON")
            print "\tCalculated GUBID"
        

    # Add GUSCID field to each fc
            arcpy.AddField_management(table,"GUSCID","TEXT")
            print "\tAdded GUSCID field"

    # Calculate GUSCID from ISO and string of USCID
            arcpy.CalculateField_management(table,"GUSCID", "!ISO_GPW4!+'_'+str(!USCID!)","PYTHON")
            print "\tCalculated GUSCID"    

        

        else:
            print iso + " skipped"
    
print "Done"


    
    
