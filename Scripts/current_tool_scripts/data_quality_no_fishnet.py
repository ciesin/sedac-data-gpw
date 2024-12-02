#-------------------------------------------------------------------------------
# Name:        module1
# Author:      Erin Doxsey-Whitfield
# Created:     02/09/2014
# Purpose:

# This script begins to identify countries where there is <No Data> to create part of the Data Quality data set

# For each country, it identifies:
#   1) No. of units in the Census table
#   2) No. of units in the boundary_2010_gridding feature class
#
#       If 2>1, there are features with no associated census count (for multiple reasons).  This will result in a <NULL> value in the gridding fc (e.g. VUT)

#   3) No. of units with negative values in the census table (by year)***

#       These units will result in <NULL> values in the associated year in the gridding fc (e.g. SVK)

#   3a) No. of units with Zero values in the census table (by year)***

#       These units will result in Zero values in the associated year in the gridding fc (e.g. SVK)

#   4) No. of units in the gridding fc with <NULL> values (by year)***      
#   4a) No. of units in the gridding fc with Zero values (by year)***


#   NOT INCLUDED HERE - TAKES LONG TIME 5) No. of pixels in the fishnet that have <NULL> (by year), CNT and CNTM***
#   NOT INCLUDED HERE - TAKES LONG TIME 5a) No. of pixels in the fishnet that have Zero (by year), CNT and CNTM***

#       To check if there are any countries that do not fit the above situations, yet still have <NULL> values in fishnet.  
#       If number of <NULL> pixels in CNT = 0, there should be no cells other than water mask creating <NULL> values in the CNTM grid.

#       Zeros in fishnet come from a) 0 in census table or water mask (for CNTM).  Noting this count for CNT and CNTM will help to identify which countries
#       have either of these cases


#   6) No. of countries that include a lookup table with an EditCode field

#       This field will be of great use in IDing units with No Data

#   7) Does water mask exist?

# *** NEED TO AMEND THIS SCRIPT TO INCLUDE ALL YEARS. CURRENTLY JUST FOR 2010


# This tool does not include the 5 large countries with their own subfolders:
# BRA, CAN, GRL, RUS, USA
# These will need to be addressed separately

# It also doesn't include VAT.mdb
# VAT doesn't have a boundary or boundary_gridding fc.

#-------------------------------------------------------------------------------


# Import libraries
import arcpy, os, csv
import datetime
startTime = datetime.datetime.now()

# Import workspace
workspace = r'\\Dataserver0\gpw\GPW4\Gridding\country\inputs'
##workspace = r'C:\Users\edwhitfi\Desktop\scratch\data_quality\inputs'
arcpy.env.workspace = workspace


# Overwrite pre-existing files
arcpy.env.overwriteOutput = True

# List File GDBs in workspace
gdbList = arcpy.ListWorkspaces("*","FileGDB")
gdbList.sort()

# define csv file
##output =r'\\Dataserver0\gpw\GPW4\Gridding\validation\data_quality.csv'
output =r'C:\Users\edwhitfi\Desktop\scratch\data_quality\inputs\data_quality.csv'

# open csv file and write header
csvFile = csv.writer(open(output,'wb'))
csvFile.writerow(("COUNTRYISO","INPUTPOP_UNITS_COUNT","BOUNDARY_GRIDDING_FC_COUNT","DIFFERENCE",
                  "NUM_UNITS_NEG_INPUTPOP","NUM_UNITS_ZERO_INPUTPOP","NUM_FCS_NULL_GRIDDING","NUM_FCS_ZERO_GRIDDING",
                 
                  "LOOKUP","EDITCODE_LOOKUP","WATERMASK"))

## Additional fields from full script: "NUM_NULL_FISHNET_CNT","NUM_NULL_FISHNET_CNTM","NUM_ZERO_FISHNET_CNT","NUM_ZERO_FISHNET_CNTM",


print "header is written"

# Iterate through gdb
for gdb in gdbList:

    iso = os.path.basename(gdb)[:-4]
    arcpy.env.workspace = gdb
    print iso


    # Have already run script for countries up to BIH... this starts script at BHR to continue.
    # Also passes KIR since it does not fit the schema (has e and w in gdb)
        
    if iso.startswith(('z'))== True:
        
     
    # 1) Get unit count in input Census table
        inputCensusList = arcpy.ListTables("*input_population") + arcpy.ListTables("*ingest*") + arcpy.ListTables("*census*")    
        if len(inputCensusList) == 1:
            for inputCensus in inputCensusList:
                result_1 = arcpy.GetCount_management(inputCensus)
                inputCensus_count = int(result_1.getOutput(0))
                print "\t" + inputCensus + ": " + str(inputCensus_count) + " units"
        elif len(inputCensusList) == 0:
            inputCensus_count = "input_population table does not exist"
            print "input_population table does not exist"
        else:
            inputCensus_count = "more than one input_population table"
            print "more than one input_population table"
            

    # 2) Get fc count in boundaries_2010_gridding fc
        griddingList = arcpy.ListFeatureClasses("*boundaries_2010_gridding")
        if len(griddingList) <> 1:
            gridding_count = "Check if gridding exists, or if there is more than 1 gridding file"
            print "\tCheck if gridding exists, or if there is more than 1 gridding file"

        else:
            for gridding in griddingList:
                result_2 = arcpy.GetCount_management(gridding)
                gridding_count = int(result_2.getOutput(0))
                print "\t" + gridding + ": " + str(gridding_count) + " fc"

        # Calculate difference between number of units in input Census table and boundaries_2010_gridding fc
        diff = gridding_count - inputCensus_count
        print "\tDifference: " + str(diff)


    # 3) No. of units with negative values in the census table (for 2010)***


        # Select all negative values in census table
        in_features = inputCensus
        out_features = r'C:\Users\edwhitfi\Desktop\scratch\data_quality\inputs' + os.sep + iso + "test.dbf"
        where_clause = ' ATOTPOPBT < 0 '
        
        arcpy.TableSelect_analysis(inputCensus, out_features, where_clause)

        # Get Count of selected negative values

        result_3 = arcpy.GetCount_management(out_features)
        inputCensus_Neg_count = int(result_3.getOutput(0))
        print "\tNumber of negative ATOTPOPBT  units in input_population: " + str(inputCensus_Neg_count)
        arcpy.Delete_management(out_features)


    # 3a) No. of units with Zero values in the census table (for 2010)***


        # Select all Zero values in census table
        in_features = inputCensus
        out_features = r'C:\Users\edwhitfi\Desktop\scratch\data_quality\inputs' + os.sep + iso + "test_zero.dbf"
        where_clause = ' ATOTPOPBT = 0 '
        
        arcpy.TableSelect_analysis(inputCensus, out_features, where_clause)

        # Get Count of selected Zero values

        result_4 = arcpy.GetCount_management(out_features)
        inputCensus_Zero_count = int(result_4.getOutput(0))
        print "\tNumber of Zero ATOTPOPBT units in input_population: " + str(inputCensus_Zero_count)
        arcpy.Delete_management(out_features)

    #   4) No. of units in the gridding fc with <NULL> values (for 2010)***
        
        # Select all <NULL> values in boundary_2010_gridding fc

        in_features = gridding
        out_features = r'C:\Users\edwhitfi\Desktop\scratch\data_quality\inputs' + os.sep + iso + "gridding_test.dbf"
        where_clause = ' E_ATOTPOPBT_2010 IS NULL'

        arcpy.Select_analysis(in_features, out_features, where_clause)

        # Get Count of selected <NULL> values

        result_5 = arcpy.GetCount_management(out_features)
        gridding_Null_count = int(result_5.getOutput(0))
        print "\tNumber of <NULL> E_ATOTPOPBT_2010 units in boundary_2010_gridding: " + str(gridding_Null_count)
        arcpy.Delete_management(out_features)

    #   4a) No. of units in the gridding fc with Zero values (for 2010)***

          
        # Select all Zero values in boundary_2010_gridding fc

        in_features = gridding
        out_features = r'C:\Users\edwhitfi\Desktop\scratch\data_quality\inputs' + os.sep + iso + "gridding_test.dbf"
        where_clause = ' E_ATOTPOPBT_2010 = 0'

        arcpy.Select_analysis(in_features, out_features, where_clause)

        # Get Count of selected Zero values

        result_6 = arcpy.GetCount_management(out_features)
        gridding_Zero_count = int(result_6.getOutput(0))
        print "\tNumber of Zero E_ATOTPOPBT_2010 units in boundary_2010_gridding: " + str(gridding_Zero_count)
        arcpy.Delete_management(out_features)

##    #   5) No. of pixels in the fishnet that have <NULL> for CNT or CNTM (for 2010)***
##
##
##
##        # Define the fishnet
##        fishnet = gdb + os.sep + iso + "_fishnet"
##
##        # Check if fishnet exists
##        if not arcpy.Exists(fishnet):
##            fishnet_Null_CNT_count = "Fishnet does not exist"
##            fishnet_Null_CNTM_count = "Fishnet does not exist"
##            fishnet_Zero_CNT_count = "Fishnet does not exist"
##            fishnet_Zero_CNTM_count = "Fishnet does not exist"
##            print "Fishnet does not exist"
##            
##        else:
##                
##            # 2010_CNT <NULL>
##            # Select all <NULL> values in the fishnet
##
##            in_features = fishnet
##            out_features = r'C:\Users\edwhitfi\Desktop\scratch\data_quality\inputs' + os.sep + iso + "fishnet_test_CNT_null.dbf"
##            where_clause = 'SUM_E_ATOTPOPBT_2010_CNT IS NULL'
##
##            arcpy.Select_analysis(in_features, out_features, where_clause)
##
##            # Get Count of selected <NULL> values
##
##            result_7 = arcpy.GetCount_management(out_features)
##            fishnet_Null_CNT_count = int(result_7.getOutput(0))
##            print "\tNumber of <NULL> SUM_E_ATOTPOPBT_2010_CNT pixels in fishnet is: " + str(fishnet_Null_CNT_count)
##            arcpy.Delete_management(out_features)
##
##            # 2010_CNTM <NULL>
##            # Select all <NULL> values in the fishnet
##
##            in_features = fishnet
##            out_features = r'C:\Users\edwhitfi\Desktop\scratch\data_quality\inputs' + os.sep + iso + "fishnet_test_CNTM_null.dbf"
##            where_clause = 'SUM_E_ATOTPOPBT_2010_CNTM IS NULL'
##
##            arcpy.Select_analysis(in_features, out_features, where_clause)
##
##            # Get Count of selected <NULL> values
##
##            result_8 = arcpy.GetCount_management(out_features)
##            fishnet_Null_CNTM_count = int(result_8.getOutput(0))
##            print "\tNumber of <NULL> SUM_E_ATOTPOPBT_2010_CNTM pixels in fishnet is: " + str(fishnet_Null_CNTM_count)
##            arcpy.Delete_management(out_features)
##
##        #   5a) No. of pixels in the fishnet that have Zero for CNT or CNTM (for 2010)***
##
##            # 2010_CNT Zero count
##            # Select all Zero values in the fishnet
##
##            in_features = fishnet
##            out_features = r'C:\Users\edwhitfi\Desktop\scratch\data_quality\inputs' + os.sep + iso + "fishnet_test_CNT_Zero.dbf"
##            where_clause = 'SUM_E_ATOTPOPBT_2010_CNT = 0'
##
##            arcpy.Select_analysis(in_features, out_features, where_clause)
##
##            # Get Count of selected Zero values
##
##            result_9 = arcpy.GetCount_management(out_features)
##            fishnet_Zero_CNT_count = int(result_9.getOutput(0))
##            print "\tNumber of Zero SUM_E_ATOTPOPBT_2010_CNT pixels in fishnet is: " + str(fishnet_Zero_CNT_count)
##            arcpy.Delete_management(out_features)
##
##            # 2010_CNTM Zero count
##            # Select all Zero values in the fishnet
##
##            in_features = fishnet
##            out_features = r'C:\Users\edwhitfi\Desktop\scratch\data_quality\inputs' + os.sep + iso + "fishnet_test_CNTM_Zero.dbf"
##            where_clause = 'SUM_E_ATOTPOPBT_2010_CNTM = 0'
##
##            arcpy.Select_analysis(in_features, out_features, where_clause)
##
##            # Get Count of selected Zero values
##
##            result_10 = arcpy.GetCount_management(out_features)
##            fishnet_Zero_CNTM_count = int(result_10.getOutput(0))
##            print "\tNumber of Zero SUM_E_ATOTPOPBT_2010_CNTM pixels in fishnet is: " + str(fishnet_Zero_CNTM_count)
##            arcpy.Delete_management(out_features)


    #   6) No. of countries that include a lookup table with an EditCode field

        # Check if a lookup table exists in the gdb
        lookupTableList = arcpy.ListTables("*lookup*")

        if len(lookupTableList) == 1:
            Lookup = 1
            print "\tLookup table exists"

        # If lookup table exists, check if an EditCode field exists in the gdb
            for lookupTable in lookupTableList:
                fieldList = arcpy.ListFields(lookupTable,"EditCode")
                if len(fieldList) == 1:
                    EditCode = 1
                    print "\tEditCode field exists in Lookup table"
                elif len(fieldList) == 0:
                    EditCode = 0
                    print "\tEditCode field DOES NOT exist in the Lookup table"
                else:
                    EditCode = 2
                    print "\tMore than one EditCode field exists"

        # Finish check for if lookup table exists
        elif len(lookupTableList) == 0:
            Lookup = 0
            EditCode = 0
            print "\tNo Lookup Table"
        else:
            Lookup = 2
            EditCode = 3
            print "\tMore than one Lookup table exists"

    #   7) Does water mask exist?
        waterMaskfc = iso + "_water_mask"
        if arcpy.Exists(waterMaskfc):
            waterMask = 1
            print "\tWater Mask exists"
        else:
            waterMask = 0
            print "\tNo Water Mask"

                
    # Print data for that gdb
        csvFile.writerow((iso,inputCensus_count,gridding_count,diff,
                          inputCensus_Neg_count,inputCensus_Zero_count,gridding_Null_count,gridding_Zero_count,
                          Lookup,EditCode, waterMask))                 

##additional fields for full script: fishnet_Null_CNT_count,fishnet_Null_CNTM_count,fishnet_Zero_CNT_count,fishnet_Zero_CNTM_count,

    else:
        print iso + " skipped"

 


print datetime.datetime.now() - startTime
print 'done'



## # Have already run script for countries up to BIH... this starts script at BHR to continue.
##    # Also passes KIR since it does not fit the schema (has e and w in gdb)
##    if gdb.startswith(("a*","bd*","be*","bf*","bg*","bhr","kir"))== False:


# Add in stuff from grids... do any pixels have <Null> that are not part of fishnet? True Zeros?  Water Zeros?



