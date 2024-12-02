#-------------------------------------------------------------------------------
# Name:        module1
# Author:      Erin Doxsey-Whitfield
# Created:     02/09/2014
# Purpose:

# This script selects features from the boundaries_gridding features classes that have <NULL> features for the E_ATOTPOPBT_2010 field

# For each country, it identifies:

# *** THIS SCRIPT IS CURRENTLY JUST FOR 2010 - DOES IT NEED TO COVER OTHER YEARS? (NO, BUT IT WOULD NEED TO COVER OTHER VARIABLES)????


# FOR CANADA

#-------------------------------------------------------------------------------


# Import libraries
import arcpy, os, csv
import datetime
startTime = datetime.datetime.now()

# Import workspace
workspace = r'\\Dataserver0\gpw\GPW4\Gridding\country\inputs\can_province\inputs'
##workspace = r'C:\Users\edwhitfi\Desktop\Notes and Instruction\Python\GPW\Selecting_Null_units_data_quality\test_folder'
arcpy.env.workspace = workspace


# Overwrite pre-existing files
arcpy.env.overwriteOutput = True

# List File GDBs in workspace
gdbList = arcpy.ListWorkspaces("can_*","FileGDB")
gdbList.sort()

# define csv file
##output =r'\\Dataserver0\gpw\GPW4\Gridding\validation\data_quality.csv'
output =r'C:\Users\edwhitfi\Desktop\Notes and Instruction\Python\GPW\Selecting_Null_units_data_quality\data_quality_null_griddingBoundaries_can_oct28.csv'

# open csv file and write header
csvFile = csv.writer(open(output,'wb'))
csvFile.writerow(("COUNTRYISO","gridding_count","gridding_Null_count", "new_gridding_Null_count"))
                 
                 
print "header is written"


# Iterate through gdb
for gdb in gdbList:

    iso = os.path.basename(gdb)[:-4]
    arcpy.env.workspace = gdb
    print iso


    # Use to skip countries that do not fit the schema (KIR: has e and w in gdb), or cause problems
           
    if iso.startswith(('kir'))== False:

        # Select gridding feature class from each .gdb

        griddingList = arcpy.ListFeatureClasses("*_gridding")
        if len(griddingList) <> 1:
            gridding_count = "Check if gridding exists, or if there is more than 1 gridding file"
            print "\tCheck if gridding exists, or if there is more than 1 gridding file"
            
        else:
            for gridding in griddingList:
                result_1 = arcpy.GetCount_management(gridding)
                gridding_count = int(result_1.getOutput(0))
                print "\t" + gridding + ": " + str(gridding_count) + " fc"


    
        # Select all <NULL> values in boundary_2010_gridding fc

        in_features = gridding
        out_features = r'C:\Users\edwhitfi\Desktop\scratch\data_quality\inputs' + os.sep + iso + "gridding_test.dbf"
        where_clause = ' E_ATOTPOPBT_2010 IS NULL'

        arcpy.Select_analysis(in_features, out_features, where_clause)

        # Get Count of selected <NULL> values

        result_2 = arcpy.GetCount_management(out_features)
        gridding_Null_count = int(result_2.getOutput(0))
        print "\tNumber of <NULL> E_ATOTPOPBT_2010 units in boundary_2010_gridding: " + str(gridding_Null_count)
        

        # If there are No <NULL> features, skip creating a new feature class
        if gridding_Null_count == 0:
            new_gridding_Null_count = "N/A"
            print "\tNew Null feature class does not need to be created"
            
        # If there are <NULL> features, select <NULL> features and create new feature class from selection
        else:

            # Set up variables to create layer from gridding feature class
            layer = iso + "_lyr"
            out_gdb_path = r'\\Dataserver0\gpw\GPW4\Gridding\global\data_quality\null_features_oct28\null_features_can_oct28.gdb'
            out_feature_class = out_gdb_path + os.sep + iso + "_null"
            
            try:

               # Make a layer from the feature class
               arcpy.MakeFeatureLayer_management(gridding,layer)

               # Sselect <NULL> features
               arcpy.SelectLayerByAttribute_management(layer, "NEW_SELECTION", 'E_ATOTPOPBT_2010 IS NULL')

               # Write the selected features to a new featureclass
               arcpy.CopyFeatures_management(layer, out_feature_class)
               print "\tNull features selected and copied to new fc"

            except:
                print arcpy.GetMessages()

            result_3 = arcpy.GetCount_management(out_feature_class)
            new_gridding_Null_count = int(result_3.getOutput(0))
            print "\tNumber of <NULL> E_ATOTPOPBT_2010 units in the new Null feature class: " + str(new_gridding_Null_count)

       
                    
        # Print data for that gdb
        csvFile.writerow((iso,gridding_count,gridding_Null_count, new_gridding_Null_count))                 

        # Delete the temp 
        arcpy.Delete_management(out_features)

    else:
        print iso + " skipped"

 


print datetime.datetime.now() - startTime
print 'done'





