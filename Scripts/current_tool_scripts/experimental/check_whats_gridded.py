# Kytt MacManus
# July 8, 2014

# Import Libraries
import arcpy, os, csv

# Define Workspace Variable
workspace = r'\\Dataserver0\gpw\GPW4\Gridding\country\inputs'

# Assign workspace environment for ArcPy
arcpy.env.workspace = workspace

# List GDBs in workspace environment
gdbs = arcpy.ListWorkspaces("*","FILEGDB")
gdbs.sort()

# define csv file
##attributes =r'\\Dataserver0\gpw\GPW4\Gridding' + os.sep + 'check_whats_gridded.csv'
### open csv file and write header
##csvFile = csv.writer(open(attributes,'wb'))
##csvFile.writerow(("COUNTRYCODE","PIXELCOUNT"))

# iterate
for gdb in gdbs:
    arcpy.env.workspace = gdb
    print gdb
##    inBoundariesList = arcpy.ListFeatureClasses("*boundaries_2010")
##    fc = inBoundariesList[0]
##    COUNTRYCODE = os.path.basename(gdb)[:-4]
##
##
##    
##    PIXELCOUNT = arcpy.GetCount_management(fc)
##    csvFile.writerow((COUNTRYCODE,PIXELCOUNT))
##    print "Added " + str(PIXELCOUNT) + " pixels for " + COUNTRYCODE
    

