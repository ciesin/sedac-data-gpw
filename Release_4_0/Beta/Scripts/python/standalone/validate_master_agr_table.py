# copy necessary input files to country gridding fgdb
# produced for beta migration
# single country input
# kmacmanus
# 5-12-15

# import libraries
import arcpy, sys, os, datetime, imp
# import the checkForField, checkFieldType, and validateSchema functions to a module called custom
custom = imp.load_source('custom',r'\\Dataserver0\gpw\GPW4\Beta\Scripts\python\functions\validateSchema.py')
# set time counter
startTime = datetime.datetime.now()
# set overwriteOutput to true
arcpy.env.overwriteOutput = True
# define input ISO
##isoText = arcpy.GetParameterAsText(0)
##iso = isoText.lower()
##adminLevel = arcpy.GetParameterAsText(1)
##grStartYear = arcpy.GetParameterAsText(2)
##grEndYear = arcpy.GetParameterAsText(3)
iso = 'ago'
adminLevel = '1'
grStartYear = '2006'
grEndYear = '2014'
print 'Processing ' + iso
arcpy.AddMessage('Processing ' + iso)
# define gridding folder workspace
workspace = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\country\inputs'
arcpy.env.workspace = workspace
# parse rootName
rootName = r'\\Dataserver0\gpw\GPW4\Beta\GrowthRate\global_agr_beta.gdb\agr_beta_v05_1'
# create a list to store validationReport items
validationReports = []
# define gridding GDB
isoGDB = r'\\Dataserver0\gpw\GPW4\Beta\GrowthRate\global_agr_beta.gdb'
# check if isoGDB exists
if not arcpy.Exists(isoGDB):
    # if not report and exit
    print isoGDB + ' does not exist'
    arcpy.AddMessage(isoGDB + ' does not exist')
    sys.exit()
# create diagnosticTable
diagnosticTemplate = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\schema_tables.gdb' + os.sep + "ingest_diagnostics"
diagnosticTable = rootName + "_agr_diagnostics"
try:
    arcpy.CopyRows_management(diagnosticTemplate,diagnosticTable)
except:
    print arcpy.GetMessages()
# define input AGR table
##agrInput = arcpy.GetParameterAsText(1)
agrInput = r'\\Dataserver0\gpw\GPW4\Beta\GrowthRate\global_agr_beta.gdb\agr_beta_v05_1'
# make a table view of the input file
agrInputView = rootName + '_growth_rate_view'
try:
    arcpy.MakeTableView_management(agrInput,agrInputView)
    print 'Created ' + agrInputView
    arcpy.AddMessage('Created ' + agrInputView)
except:
    print arcpy.GetMessages()
# validate the schema for field names and types
# define schema table
schemaTable = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\schema_tables.gdb\growth_rate'
# validate
validationResults = custom.validateSchema(agrInputView,schemaTable)
for validationResult in validationResults:
    # if the validation result fails based on type
    # then transfer the data to a field of the same
    # name and type
    if validationResult[0]==2:
        print validationResult
        arcpy.AddMessage(validationResult)
        # transfer the field to new field of the same name
        # but with the correct type
        validationField = str(validationResult[1])
        validationType = str(validationResult[2])
        tmpField = validationField + '_tmp'
        tmpCalc = '!'+validationField+'!'
        validationCalc = '!'+tmpField+'!'
        try:
            arcpy.AddField_management(agrInputView,tmpField,validationType)
            print "Added " + tmpField
        except:
            print arcpy.GetMessages()
        try:
            arcpy.CalculateField_management(agrInputView,tmpField,tmpCalc,'PYTHON')
            print "Calculated " + tmpField
        except:
            print arcpy.GetMessages()
        try:
            arcpy.DeleteField_management(agrInputView,validationField)
            print "Deleted original " + validationField
        except:
            print arcpy.GetMessages()
        try:
            if custom.checkForField(agrInputView,validationField)<>1:
                arcpy.AddField_management(agrInputView,validationField,validationType)
                print "Added new " + validationField
            else:
                print validationField + " already exists"
        except:
            print arcpy.GetMessages()
        try:
            if custom.checkForField(agrInputView,validationField)==0:
                arcpy.AddField_management(agrInputView,validationField,validationType)
                print "Added new " + validationField
                arcpy.CalculateField_management(agrInputView,validationField,validationCalc,'PYTHON')
                print "Calculated " + validationField
            else:
                arcpy.CalculateField_management(agrInputView,validationField,validationCalc,'PYTHON')
                print "Calculated " + validationField
        except:
            print arcpy.GetMessages()
        try:
            arcpy.DeleteField_management(agrInputView,tmpField)
            print 'Corrected field type for: ' + validationField
            arcpy.AddMessage('Corrected field type for: ' + validationField)
        except:
            print arcpy.GetMessages()
    # if the validation fails based on a missing field name, then human intervention is needed
    # to decide if the field needs to be added or renamed
    elif validationResult[0]==3:
        if validationResult[1]=='OBJECTID':
            pass
        else:
            print validationResult
            arcpy.AddMessage(validationResult)
            validationReports.append((1,'Schema validation failure, missing field: ' + validationResult[1],None))
# if the schema validations pass, then make a copy of the schema and load the data
agrOutTbl = rootName + 'growth_rate_1'
try:
    arcpy.CopyRows_management(schemaTable,agrOutTbl)
except:
    print arcpy.GetMessages()
try:
    arcpy.Append_management(agrOutTbl,agrInputView,'NO_TEST')
except:
    print arcpy.GetMessages() 
print 'Loaded: ' + agrOutTbl
arcpy.AddMessage('Loaded: ' + agrOutTbl)

### validate the data values
### check agrid for duplicates
##agridView = iso + '_agrid_view'
##agridDuplicates = rootName + '_growth_rate_agrid_duplicates'
##if custom.checkForDuplicates(agrOutTbl,'agrid',agridView)==1:
##    # if yes, then output the suspicious rows to a table
##    try:
##        arcpy.CopyRows_management(agridView,agridDuplicates)
##        print 'Created ' + agridDuplicates
##        arcpy.AddMessage('Created ' + agridDuplicates)
##        validationReports.append((0,'AGRID Duplicates',agridDuplicates))
##    except:
##        print arcpy.GetMessages()
##
### evaluate agrid_source
### summarize and export to new table
##agridSummary = rootName + '_growth_rate_agrid_source_summary'
##try:
##    arcpy.Frequency_analysis(agrOutTbl,agridSummary,'agrid_source')
##    print 'Created ' + agridSummary
##    arcpy.AddMessage('Created ' + agridSummary)
##except:
##    print arcpy.GetMessages()
### list to store agrid_source values
##agrid_sources = []
##if arcpy.GetCount_management(agridSummary)[0] == arcpy.GetCount_management(agrOutTbl)[0]:
##    # if these match then there is very likely a problem with agrid_source
##    print 'The number of values in agrid_source equals the number of rows...Check for error.'
##    arcpy.AddMessage('The number of values in agrid_source equals the number of rows...Check for error.')
##    validationReports.append((0,'The number of values in agrid_source equals the number of rows...Check for error.',None))
##else:
##    # create search cursor to grab agrid_source values
##    with arcpy.da.SearchCursor(agridSummary,'agrid_source') as cursor:
##        for row in cursor:
##            agrid_source = row[0]
##            # append to the sources list
##            agrid_sources.append(agrid_source)

# check the length of agrid_sources
if len(agrid_sources)==0:
    # if it is empty then write the diagnostics table, and exit
    # create and insertCursor to add rows to diagnosticTable
    insertCursor = arcpy.da.InsertCursor(diagnosticTable,['PASS','DESCRIPTION','TABLE_LOC'])
    # loop through the validationReports and write to diagnosticTable
    for validationReport in validationReports:
        print "Validation Report: " + str(validationReport)
        arcpy.AddMessage("Validation Report: " + str(validationReport))
        insertCursor.insertRow(validationReport)
    del insertCursor
    arcpy.CalculateField_management(diagnosticTable,"ISO",'"' + str(iso.upper() + '"'),"PYTHON")
    print "Import of AGR Failed...Please check diagnostics table and rerun"
    arcpy.AddMessage("Import of AGR Failed...Please check diagnostics table and rerun")
    sys.exit()
else:
    pass
    #for agrid_source in agrid_sources:
        # parse agrid_source to determine join logic



##########STOPPED TEMPORARILY TO FINISH AGR WORK






                

print 'Script complete'
print datetime.datetime.now()-startTime
