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
    fields = arcpy.ListFields(CENSUSTABLE,"a*")
    # iterate
    for field in fields:
        # define fieldName
        fieldName = field.name
        fieldName = fieldName.upper()
        # check for field in summaryTable
        fieldCheck = arcpy.ListFields(summaryTable,fieldName)
        if len(fieldCheck) == 1:
            variablePresence = "1"
            # create updateCursor
            updateCursor = arcpy.UpdateCursor(summaryTable,"ISO" + " =" + " '" + COUNTRYCODE.upper() + "'")
            # add update logic
            for row in updateCursor:
                print fieldName
                # field2 will be equal to field1 multiplied by 3.0
                row.setValue(fieldName, variablePresence)
                updateCursor.updateRow(row)
            del updateCursor
        else:
            continue
    
        
    

##  CODE BENCHMARK1 TOOK 6:47 TO EVALUATE 1 COUNTRY
##  CODE BENCHMARK2 IS USED ABOVE, IT TOOK 1:04 TO EVALUATE 1 COUNTRY
##    # list summary table fields
##    summaryFields = arcpy.ListFields(summaryTable,"a*")
##    for summaryField in summaryFields:
##        summaryFieldName = summaryField.name
##        wildCard = "*" + summaryFieldName + "*"
##        # grab census table
##        tableCensus = arcpy.ListTables("*input_population")
##        CENSUSTABLE = tableCensus[0]
##        # list fields
##        fields = arcpy.ListFields(CENSUSTABLE,wildCard)
##        if len(fields)<>1:
##            print summaryFieldName + " is not present"
##            print fields
##            variablePresence = "0"
##        else:
##            variablePresence = "1"
#################################################


print datetime.datetime.now() - startTime
