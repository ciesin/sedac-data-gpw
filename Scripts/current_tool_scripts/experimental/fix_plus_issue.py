# Kytt MacManus
# July 28, 2014
# Script to read the files on the network and summarize which census variables are present

# Import Libraries
import arcpy, os, csv
import datetime
startTime = datetime.datetime.now()
# define summary template
summaryTemplate = r'\\Dataserver0\gpw\GPW4\Gridding\validation\ancillary.gdb\variable_summary_template'
# create copy of summary template
summaryTable = r'\\Dataserver0\gpw\GPW4\Gridding\validation\ancillary.gdb' + os.sep + "input_gridding_variable_summary"
if not arcpy.Exists(summaryTable):
    try:
        arcpy.CopyRows_management(summaryTemplate,summaryTable)
        print "Copied " + summaryTable
    except:
        print arcpy.GetMessages()
else:
    print summaryTable + " already exists"
    
# Define Workspace Variable
workspace = r'\\Dataserver0\gpw\GPW4\Gridding\country\inputs'
# Assign workspace environment for ArcPy
arcpy.env.workspace = workspace
# List GDBs in workspace environment
gdbs = arcpy.ListWorkspaces("*","FILEGDB")
gdbs.sort()

### define csv file
##attributes =r'\\Dataserver0\gpw\GPW4\Gridding\validation' + os.sep + 'input_gridding_variable_summary_EXTRA_VARIABLES.csv'
### open csv file and write header
##csvFile = csv.writer(open(attributes,'wb'))
##csvFile.writerow(("COUNTRYCODE","CENSUSTABLE","VARIABLE"))

# iterate
for gdb in gdbs:
    print gdb
    arcpy.env.workspace = gdb
    # parse COUNTRYCODE
    COUNTRYCODE = os.path.basename(gdb)[:-4]
    # grab census table
    tableCensus = arcpy.ListTables("*input_population")
    CENSUSTABLE = tableCensus[0]
    # list fields
    fields = arcpy.ListFields(CENSUSTABLE,"*plus*")
    # iterate
    for field in fields:
        # define fieldName
        fieldName = field.name
        print fieldName


print datetime.datetime.now() - startTime
