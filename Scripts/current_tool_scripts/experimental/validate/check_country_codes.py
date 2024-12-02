# Kytt MacManus

# Import Libraries
import arcpy, os, csv

# Define Workspace Variable
workspace = r'\\Dataserver0\gpw\GPW4\Gridding\global\inputs\estimates_tables.gdb'

# Assign workspace environment for ArcPy
arcpy.env.workspace = workspace
arcpy.CheckOutExtension("SPATIAL")
# List GDBs in workspace environment
tables = arcpy.ListTables("*")
tables.sort()

# define csv file
attributes = r'\\dataserver0\gpw\GPW4\Scripts\current_tool_scripts\experimental\validate' + os.sep + "UCID_SUMMARY.csv"
# open csv file and write header
csvFile = csv.writer(open(attributes,'wb'))
csvFile.writerow(("ISO","UCID0"))

# iterate
for table in tables:
    ISO = table[:3]
    # create search cursor
    with arcpy.da.SearchCursor(table,"UCID0") as cursor:
        for row in cursor:
            UCID0 = row[0]
            break
    csvFile.writerow((ISO,UCID0))
    print "Added Statistics for " + ISO
    

