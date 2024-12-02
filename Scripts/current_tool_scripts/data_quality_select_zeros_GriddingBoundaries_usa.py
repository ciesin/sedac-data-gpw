#-------------------------------------------------------------------------------
# Name:        module1
# Author:      Erin Doxsey-Whitfield
# Created:     02/09/2014
# Purpose:

# This script selects features from the boundaries_gridding features classes that have features with 0
# for the E_ATOTPOPBT_2010 field

# For each country, it identifies:

# *** THIS SCRIPT IS CURRENTLY JUST FOR 2010 - DOES IT NEED TO COVER OTHER YEARS? (NO, BUT IT WOULD NEED TO COVER OTHER VARIABLES)????


# This tool does not include the 5 large countries with their own subfolders:
# BRA, CAN, GRL, RUS, USA
# These will need to be addressed separately

# It also doesn't include VAT.mdb or KIR.gdb
# VAT doesn't have a boundary or boundary_gridding fc; KIR has and e and w gridding feature and will be treated separately.

#-------------------------------------------------------------------------------


# Import libraries
import arcpy, os, csv
import datetime
startTime = datetime.datetime.now()

# Import workspace (CHANGE ME)
workspace = r'\\Dataserver0\gpw\GPW4\Gridding\country\inputs\usa_state\inputs'
##workspace = r'C:\Users\edwhitfi\Desktop\Notes and Instruction\Python\GPW\Selecting_Null_units_data_quality\test_folder'
arcpy.env.workspace = workspace


# Overwrite pre-existing files
arcpy.env.overwriteOutput = True

# List File GDBs in workspace
gdbList = arcpy.ListWorkspaces("*","FileGDB")
gdbList.sort()

# define csv file (CHANGE ME)
##output =r'\\Dataserver0\gpw\GPW4\Gridding\validation\data_quality_zero_griddingBoundaries.csv'
output =r'C:\Users\edwhitfi\Desktop\Notes and Instruction\Python\GPW\Selecting_Null_units_data_quality\data_quality_zero_griddingBoundaries_can.csv'

# open csv file and write header
csvFile = csv.writer(open(output,'wb'))
csvFile.writerow(("COUNTRYISO","gridding_count","gridding_Zero_count", "new_gridding_Zero_count"))
                 
                 
print "header is written"


# Iterate through gdb
for gdb in gdbList:

    iso = os.path.basename(gdb)[:-4]
    arcpy.env.workspace = gdb
    print iso


    # Use to skip countries that do not fit the schema (KIR: has e and w in gdb), or cause problems
           
    if iso.startswith(('kir'))== False:

        # Select gridding feature class from each .gdb

##        griddingList = arcpy.ListFeatureClasses("*boundaries_2010_gridding")
        griddingList = arcpy.ListFeatureClasses("*_gridding")
        if len(griddingList) <> 1:
            gridding_count = "Check if gridding exists, or if there is more than 1 gridding file"
            print "\tCheck if gridding exists, or if there is more than 1 gridding file"

        else:
            for gridding in griddingList:
                result_1 = arcpy.GetCount_management(gridding)
                gridding_count = int(result_1.getOutput(0))
                print "\t" + gridding + ": " + str(gridding_count) + " fc"

    
        # Select all ZERO values in boundary_2010_gridding fc

        in_features = gridding
        out_features = r'C:\Users\edwhitfi\Desktop\scratch\data_quality\inputs' + os.sep + iso + "gridding_test.dbf"
        where_clause = ' E_ATOTPOPBT_2010 =0'

        arcpy.Select_analysis(in_features, out_features, where_clause)

        # Get Count of selected ZERO values

        result_2 = arcpy.GetCount_management(out_features)
        gridding_Zero_count = int(result_2.getOutput(0))
        print "\tNumber of Zero E_ATOTPOPBT_2010 units in boundary_2010_gridding: " + str(gridding_Zero_count)
        

        # If there are No Zero features, skip creating a new feature class
        if gridding_Zero_count == 0:
            new_gridding_Zero_count = "N/A"
            print "\tNew Zero feature class does not need to be created"
            
        # If there are Zero features, select Zero features and create new feature class from selection
        else:

            # Set up variables to create layer from gridding feature class (CHANGE ME)
            layer = iso + "_lyr"
##            out_gdb_path = r'C:\Users\edwhitfi\Desktop\Notes and Instruction\Python\GPW\Selecting_Null_units_data_quality\zero_features\test_zero.gdb'
            out_gdb_path = r'\\Dataserver0\gpw\GPW4\Gridding\global\data_quality\zero_features\zero_features_usa.gdb'
            out_feature_class = out_gdb_path + os.sep + iso + "_zero"
            
            try:

               # Make a layer from the feature class
               arcpy.MakeFeatureLayer_management(gridding,layer)

               # Sselect Zero features
               arcpy.SelectLayerByAttribute_management(layer, "NEW_SELECTION", 'E_ATOTPOPBT_2010 =0')

               # Write the selected features to a new featureclass
               arcpy.CopyFeatures_management(layer, out_feature_class)
               print "\tZero features selected and copied to new fc"

            except:
                print arcpy.GetMessages()

            result_3 = arcpy.GetCount_management(out_feature_class)
            new_gridding_Zero_count = int(result_3.getOutput(0))
            print "\tNumber of Zero E_ATOTPOPBT_2010 units in the new Zero feature class: " + str(new_gridding_Zero_count)

       
                    
        # Print data for that gdb
        csvFile.writerow((iso,gridding_count,gridding_Zero_count, new_gridding_Zero_count))                 

        # Delete the temp 
        arcpy.Delete_management(out_features)

    else:
        print iso + " skipped"

 


print datetime.datetime.now() - startTime
print 'done'






