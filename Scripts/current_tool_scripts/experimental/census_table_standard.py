# Kytt MacManus
# July 8, 2014

# Import Libraries
import arcpy, os, csv
import datetime
startTime = datetime.datetime.now()
# Define Workspace Variable
workspace = r'\\Dataserver0\gpw\GPW4\Gridding\country\inputs'

# Assign workspace environment for ArcPy
arcpy.env.workspace = workspace

# List GDBs in workspace environment
gdbs = arcpy.ListWorkspaces("*","FILEGDB")
gdbs.sort()

# define csv file
attributes =r'\\Dataserver0\gpw\GPW4\Gridding' + os.sep + 'census_tables_v2.csv'
# open csv file and write header
csvFile = csv.writer(open(attributes,'wb'))
csvFile.writerow(("COUNTRYCODE","CENSUSTABLE","VARIABLE"))

# iterate
for gdb in gdbs:
    arcpy.env.workspace = gdb
    COUNTRYCODE = os.path.basename(gdb)[:-4]
    tableCensus = arcpy.ListTables("*census*")
    if len(tableCensus)==0:
        tableIngest = arcpy.ListTables("*ingest*")
        if len(tableIngest)==0:
            print gdb
            CENSUSTABLE = "MISSING"
            csvFile.writerow((COUNTRYCODE,"MISSING","MISSING"))
            continue
        else:
            for t in tableIngest:
                CENSUSTABLE = t                
    else:
        for table in tableCensus:
            CENSUSTABLE = table
    fields = arcpy.ListFields(CENSUSTABLE,"a*")
    for field in fields:
        VARIABLE = field.name
        csvFile.writerow((COUNTRYCODE,CENSUSTABLE,VARIABLE))
                      
print datetime.datetime.now() - startTime
