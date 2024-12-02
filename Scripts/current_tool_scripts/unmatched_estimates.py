# Author:      Erin Doxsey-Whitfield
# Created:     20-Oct-2014

# This script summarizes how many units and population are in the estimates_unmatched tables
#--------------------------------------------------------------------------------------------


# Import libraries
import arcpy, os, csv
import datetime
startTime = datetime.datetime.now()

# Import workspace
workspace = r'\\Dataserver0\gpw\GPW4\Gridding\country\inputs'
##workspace = r'C:\Users\edwhitfi\Desktop\scratch\estimates_unmatched'
arcpy.env.workspace = workspace

# Overwrite pre-existing files
arcpy.env.overwriteOutput = True

# List File GDBs in workspace
gdbList = arcpy.ListWorkspaces("*","FileGDB")
gdbList.sort()

# define csv file
output =r'\\Dataserver0\gpw\GPW4\Gridding\validation\esimates_unmatched.csv'
##output =r'C:\Users\edwhitfi\Desktop\scratch\estimates_unmatched\esimates_unmatched.csv'

# open csv file and write header
csvFile = csv.writer(open(output,'wb'))
csvFile.writerow(("COUNTRYISO","unmatched_units_count","unmatched_pop_count"))

print "header is written"
                  
# Iterate through gdb
for gdb in gdbList:

    iso = os.path.basename(gdb)[:-4]
    arcpy.env.workspace = gdb
    print iso

# Check if the 'estimates_unmatched' table exists
    if arcpy.Exists(iso + "_estimates_unmatched") == False:
        print "\tDoes not exist"
        unmatched_units_count = 0
        ATOTPOPBT ="N/A"
    else:
        # If it does exist, get count of how many units are in the table
        unmatched = iso + "_estimates_unmatched"
        result_2 = arcpy.GetCount_management(unmatched)
        unmatched_units_count = int(result_2.getOutput(0))
        print "\tNumber of unmatched units in the census table: " + str(unmatched_units_count)

        #If it does exists, sum the population in those units

        # Routine to check that the count fields exist
        searchFields = ["ATOTPOPBT"]
        cntFields=[]
        for field in searchFields:
            checkList = arcpy.ListFields(unmatched,field)
            if len(checkList) == 1:
                cntFields.append([field,'SUM'])
            else:
                pass

        # Create temporary table for ATOTPOPBT sums
        sum_temp_estimates_unmatched = r'C:\Users\edwhitfi\Desktop\scratch\estimates_unmatched\tempFiles\tempFiles.gdb' + os.sep + iso + "estimates_unmatched_temp"    

        if not len(cntFields) == 0:
            arcpy.Statistics_analysis(unmatched,sum_temp_estimates_unmatched,cntFields)
             # Get a list of fields from the new in-memory table
            flds = arcpy.ListFields(sum_temp_estimates_unmatched)
            # Open a Search Cursor using field name
            for fld in flds:
                search = arcpy.SearchCursor(sum_temp_estimates_unmatched)
                
                for row in search:
                    if fld.name == "SUM_ATOTPOPBT":
                        #Get the first row with sum value
                        ATOTPOPBT = row.getValue(fld.name)
                        print "\tTotal pop in unmached units: " + str(ATOTPOPBT)

    # Write to CSV
    csvFile.writerow([iso,unmatched_units_count,ATOTPOPBT])
                    

print "done"
