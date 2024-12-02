# Kytt MacManus
# January 5, 2014

# Import Libraries
import arcpy, os, csv

# Define Workspace Variable
workspace = r'E:\gpw\usa_state_v2\states'

# Assign workspace environment for ArcPy
arcpy.env.workspace = workspace

# List GDBs in workspace environment
gdbs = arcpy.ListWorkspaces("*","FILEGDB")
gdbs.sort()

# define csv file
attributes =workspace + os.sep + 'unit_count.csv'
# open csv file and write header
csvFile = csv.writer(open(attributes,'wb'))
csvFile.writerow(("COUNTRYCODE","PIXELCOUNT"))

# iterate
for gdb in gdbs:
    arcpy.env.workspace = gdb
    inBoundariesList = arcpy.ListFeatureClasses("*fishnet")
    fc = inBoundariesList[0]
    COUNTRYCODE = os.path.basename(gdb)[:-4]
    PIXELCOUNT = arcpy.GetCount_management(fc)
    csvFile.writerow((COUNTRYCODE,PIXELCOUNT))
    print "Added " + str(PIXELCOUNT) + " pixels for " + COUNTRYCODE
    

