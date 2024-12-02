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
### set overwriteOutput to true
##arcpy.env.overwriteOutput = True
# define input ISO
##isoText = arcpy.GetParameterAsText(0)
##iso = isoText.lower()
iso = 'ago'
print 'Processing ' + iso
arcpy.AddMessage('Processing ' + iso)

# define gridding folder workspace
workspace = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\country\inputs'
arcpy.env.workspace = workspace

# request user input for parameters
##sexData = arcpy.GetParameterAsText(1)
##inputPopTable = arcpy.GetParameterAsText(2)
##ingestTab = arcpy.GetParameterAsText(3)
##adminLevel = arcpy.GetParameterAsText(4)
##estimateYear = arcpy.GetParameterAsText(5)
##yearField = arcpy.GetParameterAsText(6)
##lookupTableExist = arcpy.GetParameterAsText(7)
##lookupTable = arcpy.GetParameterAsText(8)
sexData = 'true'
inputPopTable = r'\\Dataserver0\gpw\GPW4\Beta\Preprocessing\Country\AGO\Ingest\Census\AGO_2014_ingest_admin2.xlsx'
ingestTab = 'ago_admin2_census_2014'
adminLevel = '2'
estimateYear = '2014'
yearField = 'CENSUS_YEAR'
lookupTableExist = 'false'
lookupTable = None
# create a list to store validationReport items
validationReports = []
# parse rootName
rootName = workspace + os.sep + iso + '.gdb' + os.sep + iso + '_admin' + adminLevel + '_' + estimateYear

# create file geodatabase
isoGDB = workspace + os.sep + iso + '.gdb'
if not arcpy.Exists(isoGDB):
    try:
        arcpy.CreateFileGDB_management(workspace,iso)
        print 'Created gridding file GDB'
        arcpy.AddMessage('Created gridding file GDB ')
    except:
        print arcpy.GetMessages
else:
    print 'The file GDB already exists.  Find out why and delete if necessary before running this tool'
    arcpy.AddMessage('The file GDB already exists.  Find out why and delete if necessary before running this tool')
##    sys.exit()
    
# create diagnosticTable
diagnosticTemplate = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\schema_tables.gdb' + os.sep + "ingest_diagnostics"
if not sexData == 'true':
    diagnosticTable = rootName + "_ingest_diagnostics"
else:
    diagnosticTable = rootName + "_ingest_sex_variable_diagnostics"
try:
    arcpy.CopyRows_management(diagnosticTemplate,diagnosticTable)
except:
    print arcpy.GetMessages()
# copy the input raw population table and run validations
try:
    if not sexData == 'true':
        inRawTable = rootName + '_raw_population'
    else:
        inRawTable = rootName + '_raw_sex_variables'
    arcpy.ExcelToTable_conversion(inputPopTable,inRawTable,ingestTab)
    print 'Copied ' + ingestTab + ' to ' + inRawTable
    arcpy.AddMessage('Copied ' + ingestTab + ' to ' + inRawTable)
except:
    print arcpy.GetMessages()

# check if there are duplicate USCIDs
uscidView = os.path.basename(rootName) + "_uscid_duplicates"
if not sexData == 'true':
    uscidDuplicates = rootName + "_uscid_duplicates"
else:
    uscidDuplicates = rootName + "_uscid_duplicates_sex_variables"
if int(custom.checkForDuplicates(inRawTable,"USCID",uscidView))==1:
    # if yes, then output the suspicious rows to a table
    try:
        arcpy.CopyRows_management(uscidView,uscidDuplicates)
        print "Created " + uscidDuplicates
        arcpy.AddMessage("Created " + uscidDuplicates)
        validationReports.append((0,"USCID Duplicates",uscidDuplicates))
    except:
        print arcpy.GetMessages()
    
##########check that adminLevel corresponds to the number of UCADMINS and NAMES########## 
# are there the same number of UCADMIN fields as NAME fields?
# if not, then validation fails
if not len(arcpy.ListFields(inRawTable,'NAME*'))==len(arcpy.ListFields(inRawTable,'UCADMIN*')):
    print 'Check table, the number of NAME fields does not match the number of UCADMIN fields'
    arcpy.AddMessage('Check table, the number of NAME fields does not match the number of UCADMIN fields')
    validationReports.append((1,"NAME or UCADMIN is missing. Check and rerun.",None))
# if the number of fields are the same, then does that number correspond to what the user input for the adminLevel?
# if not, then validation fails
# define admin check as the number input by the user + 1 to account for admin0
adminCheck = int(adminLevel) + 1
if not len(arcpy.ListFields(inRawTable,'NAME*'))==adminCheck:
    print 'Check table, the number of NAME fields does not match what you input for the administrative level'
    arcpy.AddMessage('Check table, the number of NAME fields does not match what you input for the administrative level')
    validationReports.append((1,"The number of levels does not match what was input for file name. Check and rerun.",None))
##########check that estimateYear corresponds to the year captured in the data##########
# check if the yearField is already in correct format and exists
if yearField == 'RPOPYEAR':
    if custom.checkForField(inRawTable,'RPOPYEAR')==1:
        pass
    else:
        print 'The input yearField: ' + yearField + ' does not exist in the table'
        arcpy.AddMessage('The input yearField: ' + yearField + ' does not exist in the table')
        sys.exit()
else:
    if custom.checkForField(inRawTable,yearField)==1:
        pass
    else:
        print 'The input yearField: ' + yearField + ' does not exist in the table'
        arcpy.AddMessage('The input yearField: ' + yearField + ' does not exist in the table')
        sys.exit()  
# next run frequency analysis on the provided yearField in case it is not unique
try:
    yearTable = 'in_memory' + os.sep + iso + '_year'
    arcpy.Frequency_analysis(inRawTable,yearTable,yearField)
    print 'Created ' + yearTable
    arcpy.AddMessage('Created ' + yearTable)
except:
    print arcpy.GetMessages()
# getCount of the number of rows in yearTable, if more than 1 then further analysis is needed
if int(arcpy.GetCount_management(yearTable)[0])<>1:
    yearList = []
    freqList = []
    # we need to select the most frequent year
    with arcpy.da.SearchCursor(yearTable,[yearField,'FREQUENCY']) as cursor:       
        for row in cursor:            
            yearList.append(row[0])
            freqList.append(row[1])
    maxFreq = max(freqList)
    maxPosition = freqList.index(maxFreq)
    yearValue = yearList[maxPosition]
else:
    with arcpy.da.SearchCursor(inRawTable,[yearField]) as cursor:       
        for row in cursor:
            yearValue = row[0]
# now that we have specified yearValue, check that it matches the input year
# if not validation fails
if not str(yearValue)==estimateYear:
    print 'Check table, the specified year value does not match the year value in the input table'
    arcpy.AddMessage('Check table, the specified year value does not match the year value in the input table')
    validationReports.append((1,'Check table, the specified year value does not match the year value in the input table',None))                             


#########evaluate ATOTPOPBT field for negative values and extract rows if needed##########
# check if inRawTable has ATOTPOPBT field
if custom.checkForField(inRawTable,'ATOTPOPBT')==1:
    # need to check outPop1Tbl to see if there are an NEGATIVE values in ATOTPOPBT
    # if there are negative values, then extract them
    negClause = 'ATOTPOPBT<0'
    negValueView = os.path.basename(rootName) + '_atotpopbt_negatives'
    outNegTbl = rootName + '_atotpopbt_negatives'
    posClause = 'ATOTPOPBT>0'
    posValueView = os.path.basename(rootName) + '_atotpopbt_positives'
    if not sexData == 'true':
        outPop1Tbl = rootName + '_input_population_v01'
    else:
        outPop1Tbl = rootName + '_input_sex_variables_v01'    
    # run checkTableCondition, if it fails set outPop1Tbl to inRawTable
    # failure means that there aren't any negative value rows, no need to process further
    if int(custom.checkTableCondition(inRawTable,negClause,negValueView,outNegTbl,posClause,posValueView,outPop1Tbl)[0])==0:
        # create outPop1Tbl
        arcpy.CopyRows_management(inRawTable,outPop1Tbl)
else:
    print 'ATOTPOPBT Field is not present in ' + inRawTable
    arcpy.AddMessage('ATOTPOPBT Field is not present in ' + inRawTable)
    validationReports.append((1,'ATOTPOPBT Field is not present. Check inputs',None))

# check if ISO exists
if custom.checkForField(outPop1Tbl,'ISO')==1:
    # if yes, then pass
    pass
else:
    # otherwise add and calculate
    try:
        arcpy.AddField_management(outPop1Tbl,'ISO','TEXT','#','#',5)
        arcpy.CalculateField_management(outPop1Tbl,'ISO','"'+iso.upper()+'"','PYTHON')
        print 'Added and calculated ISO'
        arcpy.AddMessage('Added and calculated ISO')
    except:
        print arcpy.GetMessages()
# add and calculate RPOPYEAR as correct year name if needed
# check if the field already exists
if not custom.checkForField(outPop1Tbl,'RPOPYEAR')==1:
    try:
        # perform calculation
        arcpy.AddField_management(outPop1Tbl,'RPOPYEAR','SHORT')
        arcpy.CalculateField_management(outPop1Tbl,'RPOPYEAR','!'+yearField+'!','PYTHON')
        arcpy.DeleteField_management(outPop1Tbl,yearField)
        print 'Added and calculated RPOPYEAR'
        arcpy.AddMessage('Added and calculated RPOPYEAR')
    except:
        print arcpy.GetMessages()

# if we pass this check we can select the appropriate schema table and validate
if not sexData == 'true':
    schemaTable = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\schema_tables.gdb' + os.sep + 'totalpop_admin' + adminLevel
else:
    schemaTable = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\schema_tables.gdb' + os.sep + 'sex_admin' + adminLevel

validationResults = custom.validateSchema(outPop1Tbl,schemaTable)
# custom.validateSchema captures missing field names and incorrect field types
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
        tmpField = validationField + "_tmp"
        tmpCalc = '!'+validationField+'!'
        validationCalc = '!'+tmpField+'!'
        try:
            arcpy.AddField_management(outPop1Tbl,tmpField,validationType)
            arcpy.CalculateField_management(outPop1Tbl,tmpField,tmpCalc,"PYTHON")
            arcpy.DeleteField_management(outPop1Tbl,validationField)
            arcpy.AddField_management(outPop1Tbl,validationField,validationType)
            arcpy.CalculateField_management(outPop1Tbl,validationField,validationCalc,"PYTHON")
            arcpy.DeleteField_management(outPop1Tbl,tmpField)
            print 'Corrected field type for: ' + validationField
            arcpy.AddMessage('Corrected field type for: ' + validationField)
        except:
            print arcpy.GetMessages()
    # if the validation fails based on a missing field name, then human intervention is needed
    # to decide if the field needs to be added or renamed
    elif validationResult[0]==3:
        print validationResult
        arcpy.AddMessage(validationResult)
        validationReports.append((1,"Schema validation failure, missing field: " + validationResult[1],None))
    
# if the validations pass, then make a copy of the schema and load the data
if not sexData == 'true':
    outPopTable = rootName + '_input_population'
else:
    outPopTable = rootName + '_input_sex_variables'
try:
    arcpy.CopyRows_management(schemaTable,outPopTable)
except:
    print arcpy.GetMessages()
try:
    arcpy.Append_management(outPop1Tbl,outPopTable,"NO_TEST")
except:
    print arcpy.GetMessages() 
print 'Loaded: ' + outPopTable
arcpy.AddMessage('Loaded: ' + outPopTable)

# the input population must have a UBID joined
# if it is on inRawTable, then get it from there
if not sexData == 'true':
    if custom.checkForField(inRawTable,"UBID")==1:
        try:
            arcpy.JoinField_management(outPopTable,"USCID",inRawTable,"USCID","UBID")
        except:
            print arcpy.GetMessages()
        print "Joined UBID"
        arcpy.AddMessage("Joined UBID")
    # otherwise require a lookup table
    elif lookupTable == None:
        print "Lookup table is required to add UBID"
        arcpy.AddMessage("Lookup table is required to add UBID")
        sys.exit()
    else:
        # check to make sure there are no duplicate UBIDs in joinTable
        lookupView = os.path.basename(lookupTable) + "_duplicates"
        if int(custom.checkForDuplicates(lookupTable,"UBID",lookupView))==1:
            # if there are duplicates write them to an output table
            ubidDuplicates = lookupTable + "_UBID_duplicates"
            try:
                arcpy.CopyRows_management(lookupView,ubidDuplicates)
                print "There are duplicate UBIDs, check output table"
                arcpy.AddMessage("There are duplicate UBIDs, check output table")
                validationReports.append((0,"UBID Duplicates",ubidDuplicates))
            except:
                print arcpy.GetMessages()
        try:
            arcpy.JoinField_management(outPopTable,"USCID",lookupTable,"USCID","UBID")
        except:
            print arcpy.GetMessages()
        print "Joined UBID"
        arcpy.AddMessage("Joined UBID")

    # check if there are any null UBIDs in final table
    nullUBIDView = os.path.basename(rootName) + "_null_ubids"
    nullUBIDTbl = rootName + "_null_ubids"
    nullExp = "UBID IS NULL"
    if int(arcpy.GetCount_management(arcpy.MakeTableView_management(outPopTable,nullUBIDView,nullExp))[0])>0:
        # if yes then write them out
        try:
            arcpy.CopyRows_management(nullUBIDView,nullUBIDTbl)
        except:
            print arcpy.GetMessages()
        print "There are null UBIDs, Check and rerun."
        arcpy.AddMessage("There are null UBIDs, Check and rerun.")
        validationReports.append((0,"There are null UBIDs, Check and rerun. Does it need a POPCONTEXT field?",nullUBIDTbl))
        

# delete any temp input population versions
arcpy.env.workspace = workspace + os.sep + iso + '.gdb'
if not sexData == 'true':
    delTbls = arcpy.ListTables('*population_v*')
else:
    delTbls = arcpy.ListTables('*sex_variables_v*')
for delTbl in delTbls:
    arcpy.Delete_management(delTbl)
# if the length of validationReports is > 0 then we should write an output table
if len(validationReports)>0:
    # create and insertCursor to add rows to diagnosticTable
    insertCursor = arcpy.da.InsertCursor(diagnosticTable,['PASS','DESCRIPTION','TABLE_LOC'])
    # loop through the validationReports and write to diagnosticTable
    for validationReport in validationReports:
        print "Validation Report: " + str(validationReport)
        insertCursor.insertRow(validationReport)
    del insertCursor
    arcpy.CalculateField_management(diagnosticTable,"ISO",'"' + str(iso.upper() + '"'),"PYTHON")

print 'Script complete'
print datetime.datetime.now()-startTime
