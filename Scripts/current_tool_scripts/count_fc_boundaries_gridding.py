#-------------------------------------------------------------------------------
# Name:        module1
# Author:      Erin Doxsey-Whitfield
# Created:     28/08/2014
# Purpose:     To count the total number of features in the boundary and
#               boundary_gridding feature classes within the Gridding/inputs gdb
#
#               If boundary_gridding fc has fewer features than boundary fc, it
#               indicates that there were additional units in the boundary that
#               were not included in the census table.  These areas will be
#               marked as <No Data>.
#
#               This script helps us identify countries we need to look at for
#               the No Data layer
#-------------------------------------------------------------------------------

# This tool does not include the 5 large countries with their own subfolders:
# BRA, CAN, GRL, RUS, USA
# These will need to be addressed separately



# Import libraries
import arcpy, os, csv
import datetime
startTime = datetime.datetime.now()

# Import workspace
workspace = r'\\Dataserver0\gpw\GPW4\Gridding\country\inputs'
##workspace = r'C:\Users\edwhitfi\Desktop\scratch\fc_count_test\inputs'
arcpy.env.workspace = workspace


# List File GDBs in workspace
gdbList = arcpy.ListWorkspaces("*","FileGDB")
gdbList.sort()


# define csv file
##output =r'\\Dataserver0\gpw\GPW4\Gridding\validation\boundary_gridding_fc_count.csv'
output =r'\\Dataserver0\gpw\GPW4\Gridding\validation\boundary_gridding_fc_count_Dec1.csv'
##output =r'C:\Users\edwhitfi\Desktop\scratch\fc_count_test\inputs\boundary_gridding_fc_count.csv'

# open csv file and write header
csvFile = csv.writer(open(output,'wb'))
csvFile.writerow(("COUNTRYISO","BOUNDARY_FC_COUNT","BOUNDARY_GRIDDING_FC_COUNT","DIFFERENCE"))

print "header is written"

# Iterate through gdb
for gdb in gdbList:
    iso = os.path.basename(gdb)[:-4]
    print iso
    arcpy.env.workspace = gdb
   
# Get fc count in boundaries_2010 fc
    boundaryList = arcpy.ListFeatureClasses("*boundaries_2010")      
    for boundary in boundaryList:
        result_1 = arcpy.GetCount_management(boundary)
        boundary_count = int(result_1.getOutput(0))
        print "\t" + boundary + ": " + str(boundary_count) + " fc"

# Get fc count in boundaries_2010_gridding fc
    griddingList = arcpy.ListFeatureClasses("*boundaries_2010_gridding")
    for gridding in griddingList:
        result_2 = arcpy.GetCount_management(gridding)
        gridding_count = int(result_2.getOutput(0))
        print "\t" + gridding + ": " + str(gridding_count) + " fc"

    diff = boundary_count - gridding_count
    print "\tDifference: " + str(diff)                                    
                                        
    csvFile.writerow((iso,boundary_count,gridding_count,diff)) 

print datetime.datetime.now() - startTime
print 'done'






