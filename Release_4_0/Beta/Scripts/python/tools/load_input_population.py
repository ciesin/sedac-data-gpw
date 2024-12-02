# copy necessary input files to country gridding fgdb
# produced for beta migration
# single country input
# kmacmanus
# 5-12-15

## REASONS TO FAIL VALIDATION
## IF VALIDATION FAILS THEN THE FINAL POP TABLE IS NOT WRITTEN
##1) USCID Duplicates
##2) The number of NAME fields does not match what was input for file name.
##3) The specified year value does not match the year value in the input table
##4) Schema validation failure, missing field:
##5) Append Fails
##6) UBID Duplicates
##7) Need to correct null UBIDs. Either add POP_CONTEXT or fill in proper UBID

# import libraries
import arcpy, sys, os, datetime, imp
# import the checkForField, checkFieldType, and validateSchema functions to a module called custom
custom = imp.load_source('custom',r'\\Dataserver0\gpw\GPW4\Beta\Scripts\python\functions\validateSchema.py')
# set time counter
startTime = datetime.datetime.now()
# set overwriteOutput to true
arcpy.env.overwriteOutput = True
# define input ISO
isoText = arcpy.GetParameterAsText(0)
iso = isoText.lower()
##iso = 'ago'
print 'Processing ' + iso
arcpy.AddMessage('Processing ' + iso)

# define gridding folder workspace
workspace = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\country\inputs'
arcpy.env.workspace = workspace

# request user input for parameters
inputPopTable = arcpy.GetParameterAsText(1)
ingestTab = arcpy.GetParameterAsText(2)
adminLevel = arcpy.GetParameterAsText(3)
estimateYear = arcpy.GetParameterAsText(4)
yearField = arcpy.GetParameterAsText(5)
lookupTableExist = arcpy.GetParameterAsText(6)
lookupTable = arcpy.GetParameterAsText(7)

##inputPopTable = r'\\Dataserver0\gpw\GPW4\Beta\Preprocessing\Country\AGO\Ingest\Census\AGO_2014_ingest_admin2.xlsx'
##ingestTab = 'ago_admin2_census_2014'
##adminLevel = '2'
##estimateYear = '2014'
##yearField = 'CENSUS_YEAR'
##lookupTableExist = 'false'
##lookupTable = None

# create a list to store validationReport items
validationReports = []
# parse rootName
rootName = workspace + os.sep + iso + '.gdb' + os.sep + iso + '_admin' + adminLevel + '_' + estimateYear
## REVISE SO THAT FGDB CAN EXIST WITHOUT SYS.EXIT
# create file geodatabase
isoGDB = workspace + os.sep + iso + '.gdb'
try:
    arcpy.CreateFileGDB_management(workspace,iso)
    print 'Created gridding file GDB'
    arcpy.AddMessage('Created gridding file GDB ')
except:
    print 'The file GDB already exists.  Find out why and delete if necessary before running this tool'
    arcpy.AddMessage('The file GDB already exists.  Find out why and delete if necessary before running this tool')
    sys.exit()

# copy the input raw population table and run validations
try:
    inRawTable = rootName + '_raw_population'
    # check to see if the table is from FGDB or Excel
    if inputPopTable[-4:]=="xlsx":
        inputFormat = "Excel"
        arcpy.ExcelToTable_conversion(inputPopTable,inRawTable,ingestTab)
    elif inputPopTable[-4:]==".xls":
        inputFormat = "Excel"
        arcpy.ExcelToTable_conversion(inputPopTable,inRawTable,ingestTab)
    else:
        inputFormat = "FGDBT"
        arcpy.CopyRows_management(inputPopTable,inRawTable)
    print 'Copied ' + ingestTab + ' to ' + inRawTable
    arcpy.AddMessage('Copied ' + ingestTab + ' to ' + inRawTable)
except:
    print arcpy.GetMessages()

# create processMetadata
processMetadataTemplate = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\schema_tables.gdb' + os.sep + "process_metadata"
processMetadataTable = rootName + "_ingest_metadata"
try:
    arcpy.CopyRows_management(processMetadataTemplate,processMetadataTable)
except:
    print arcpy.GetMessages()
# populate the table with input parameters
metadataParams = (None,iso,inputPopTable,inputFormat,ingestTab,adminLevel,
                  estimateYear,lookupTable,str(datetime.datetime.now()))
cursor = arcpy.da.InsertCursor(processMetadataTable,"*")
cursor.insertRow(metadataParams)
# Delete cursor object
del cursor

# check if there are duplicate USCIDs
uscidView = os.path.basename(rootName) + "_uscid_duplicates"
uscidDuplicates = rootName + "_uscid_duplicates"
if int(custom.checkForDuplicates(inRawTable,"USCID",uscidView))==1:
    # if yes, then output the suspicious rows to a table
    try:
        arcpy.CopyRows_management(uscidView,uscidDuplicates)
        print "Created " + uscidDuplicates
        arcpy.AddMessage("Created " + uscidDuplicates)
        validationReports.append((0,"Check, correct, and rerun: USCID Duplicates",uscidDuplicates))
    except:
        print arcpy.GetMessages()
    
##########check that adminLevel corresponds to the number of UCADMINS and NAMES##########
# the commented block here seems redundant, probably not needed####################################
### are there the same number of UCADMIN fields as NAME fields?
### if not, then validation fails
##if not len(arcpy.ListFields(inRawTable,'NAME*'))==len(arcpy.ListFields(inRawTable,'UCADMIN*')):
##    print 'Check table, the number of NAME fields does not match the number of UCADMIN fields'
##    arcpy.AddMessage('Check table, the number of NAME fields does not match the number of UCADMIN fields')
##    validationReports.append((1,"A NAME or UCADMIN field is missing. Check the table, correct, and rerun.",None))
### if the number of fields are the same, then does that number correspond to what the user input for the adminLevel?
### if not, then validation fails
# define admin check as the number input by the user + 1 to account for admin0
adminCheck = int(adminLevel) + 1
if not len(arcpy.ListFields(inRawTable,'NAME*'))==adminCheck:
    print 'Check table, the number of NAME fields does not match what you input for the administrative level'
    arcpy.AddMessage('Check table, the number of NAME fields does not match what you input for the administrative level')
    validationReports.append((1,"The number of NAME fields does not match what was input for file name. Check, correct, and rerun.",None))
##########check that estimateYear corresponds to the year captured in the data##########
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
if not str(int(yearValue))==str(int(estimateYear)):
    print 'Check table, the specified year value does not match the year value in the input table'
    arcpy.AddMessage('Check table, the specified year value does not match the year value in the input table')
    validationReports.append((1,'Check, correct, and rerun: the specified year value does not match the year value in the input table',None))                             

# create a version of the input pop table which can be altered
outPop1Tbl = rootName + '_input_population_v01'
try:
    arcpy.CopyRows_management(inRawTable,outPop1Tbl)
except:
    print arcpy.GetMessages()   

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
# add logic here to discriminate between TOTPOP, SEX, AGE, and UR Tables
schemaTable = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\schema_tables.gdb' + os.sep + 'total_pop_admin' + adminLevel
validationResults = custom.validateSchema(outPop1Tbl,schemaTable)
# custom.validateSchema captures missing field names and incorrect field types
uscidChange = False
for validationResult in validationResults:
    # if the validation result fails based on type
    # then transfer the data to a field of the same
    # name and type
    if validationResult[0]==2:
        print validationResult
        arcpy.AddMessage(validationResult)
        arcpy.AddMessage(str(validationResult[1]))
        # if the USCID field changes type we need to know in order to properly join UBIDs later
        if str(validationResult[1]) == "USCID":
            uscidChange = True
            arcpy.AddMessage("uscidChange = " + str(uscidChange))         
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
        # if the field in question is "POP_CONTEXT" then simply pass
        # the reason is that some tables may not have pop_context at the start, which is ok
        if validationResult[1]=="POP_CONTEXT":
            pass
        else:
            print validationResult
            arcpy.AddMessage(validationResult)
            validationReports.append((1,"Check, correct, and rerun: Schema validation failure, missing field: " + validationResult[1],None))

#########evaluate ATOTPOPBT field for negative values and extract rows and recode as null if needed##########
# check if inRawTable has ATOTPOPBT field
if custom.checkForField(outPop1Tbl,'ATOTPOPBT')==1:
    # need to check to see if there are an NEGATIVE values in ATOTPOPBT
    negExp = 'ATOTPOPBT<0'
    negValueView = os.path.basename(rootName) + '_atotpopbt_negatives'
    if int(arcpy.GetCount_management(arcpy.MakeTableView_management(outPop1Tbl,negValueView,negExp))[0])>0:
        # if there are negative values, then extract them
        outNegTbl = rootName + '_atotpopbt_negatives'        
        try:
            arcpy.CopyRows_management(negValueView,outNegTbl)
        except:
            print arcpy.GetMessages()
        # next recode them as null
        try:
            arcpy.CalculateField_management(negValueView,"ATOTPOPBT",None)
        except:
            print arcpy.GetMessages()            
    
# when the validations complete make a copy of the schema and load the data
outPop2Tbl = rootName + '_input_population_v02'
try:
    arcpy.CopyRows_management(schemaTable,outPop2Tbl)
except:
    print arcpy.GetMessages()
try:
    arcpy.Append_management(outPop1Tbl,outPop2Tbl,"NO_TEST")
    print 'Loaded: ' + outPop2Tbl
    arcpy.AddMessage('Loaded: ' + outPop2Tbl)
except:
    print arcpy.GetMessages() 
    arcpy.AddMessage(arcpy.GetMessages())
    validationReports.append((0,"Check, correct, and rerun: Append Failed, it might be due to field length. Check" ))

# the input population must have a UBID joined
# first need to update USCID in case it is the wrong type
if uscidChange == True:
    # if so add a tmpid type double and calculate
    try:
        arcpy.AddField_management(outPop2Tbl,"TMPID","DOUBLE")
        # could replace DOUBLE with actual original field type
        arcpy.CalculateField_management(outPop2Tbl,"TMPID","!USCID!","PYTHON")
        arcpy.AddMessage("Calculated TMPID")
    except:
        print arcpy.GetMessages()
    joinField = "TMPID"
else:
    joinField = "USCID"
# if it is on inRawTable, then get it from there
if custom.checkForField(inRawTable,"UBID")==1:
    try:
        arcpy.JoinField_management(outPop2Tbl,joinField,inRawTable,"USCID","UBID")
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
    try:
        arcpy.JoinField_management(outPop2Tbl,joinField,lookupTable,"USCID","UBID")
        print "Joined UBID"
        arcpy.AddMessage("Joined UBID")
    except:
        print arcpy.GetMessages()
# if TMPID was added then it must be deleted
if uscidChange == True:
    try:
        arcpy.DeleteField_management(outPop2Tbl,"TMPID")
    except:
        print arcpy.GetMessages()
        
        
# check to make sure there are no duplicate UBIDs
dupView = os.path.basename(outPop2Tbl) + "_ubid_duplicates"
if int(custom.checkForDuplicates(outPop2Tbl,"UBID",dupView))==1:
    # if there are duplicates write them to an output table
    ubidDuplicates = rootName + "_duplicate_ubids"
    try:
        arcpy.CopyRows_management(dupView,ubidDuplicates)
        print "There are duplicate UBIDs, check output table"
        arcpy.AddMessage("There are duplicate UBIDs, check output table")
        validationReports.append((0,"Check, correct, and rerun: there are UBID Duplicates",ubidDuplicates))
    except:
        print arcpy.GetMessages()

# check if there are any null UBIDs
nullUBIDView = os.path.basename(rootName) + "_null_ubids"
nullUBIDTbl = rootName + "_null_ubids"
nullExp = "UBID IS NULL"
if int(arcpy.GetCount_management(arcpy.MakeTableView_management(outPop2Tbl,nullUBIDView,nullExp))[0])>0:
    # if yes then write them out
    try:
        arcpy.CopyRows_management(nullUBIDView,nullUBIDTbl)
    except:
        print arcpy.GetMessages()
    print "There are null UBIDs, Check and add popcontext or rerun."
    arcpy.AddMessage("There are null UBIDs, Check and add popcontext or rerun")
    ###########evaluate POPCONTEXT field on Null UBIDS and extract rows if needed##########
    if custom.checkForField(nullUBIDTbl,'POP_CONTEXT')==1:
        # if yes then create a condition to check if there are any
        # null popcontext rows 
        popContextExp = 'POP_CONTEXT IS NULL'
        popContextView = os.path.basename(nullUBIDTbl) + '_missing_popcontext'
        missingPopContextTbl = nullUBIDTbl + '_missing_popcontext'
        if int(arcpy.GetCount_management(arcpy.MakeTableView_management(nullUBIDTbl,popContextView,popContextExp))[0])>0:
            # if yes, then write these rows to a table
            try:
                arcpy.CopyRows_management(popContextView,missingPopContextTbl)
            except:
                print arcpy.GetMessages()
            validationReports.append((1,'Need to correct null UBIDs. Either add POP_CONTEXT or fill in proper UBID',missingPopContextTbl))
        else:
            # otherwise rename the nullUBIDTBL
            try:
                contextTbl = rootName + "_pop_context"
                arcpy.Rename_management(nullUBIDTbl,contextTbl)
            except:
                print arcpy.GetMessages()
    # if the popcontext field is missing, then we might need to check, so add message
    # might not actually ever occur!!
    else:
        missingPopContextTbl = nullUBIDTbl + '_missing_popcontext'
        try:
            arcpy.CopyRows_management(nullUBIDTbl,missingPopContextTbl)
        except:
            print arcpy.GetMessages()
        validationReports.append((1,'Need to correct null UBIDs. Either add POP_CONTEXT or fill in proper UBID',missingPopContextTbl))

# if the length of validationReports is > 0 then write an output table
if len(validationReports)>0:
    # create diagnosticTable
    diagnosticTemplate = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\schema_tables.gdb' + os.sep + "ingest_diagnostics"
    diagnosticTable = rootName + "_ingest_diagnostics"
    try:
        arcpy.CopyRows_management(diagnosticTemplate,diagnosticTable)
    except:
        print arcpy.GetMessages()
    # create and insertCursor to add rows to diagnosticTable
    insertCursor = arcpy.da.InsertCursor(diagnosticTable,['PASS','DESCRIPTION','TABLE_LOC'])
    # loop through the validationReports and write to diagnosticTable
    for validationReport in validationReports:
        print "Validation Report: " + str(validationReport)
        insertCursor.insertRow(validationReport)
    del insertCursor
    arcpy.CalculateField_management(diagnosticTable,"ISO",'"' + str(iso.upper() + '"'),"PYTHON")
# otherwise create the final table
else:
    # copy final table
    outPopTable = rootName + '_input_population'
    try:
        arcpy.CopyRows_management(outPop2Tbl,outPopTable)
        print "Created " + outPopTable
    except:
        print arcpy.GetMessages()
    # strip whitespace from all string fields in table
    try:
        custom.stripWhiteSpace(outPopTable)
    except:
        print arcpy.GetMessages()
    # delete any temp input population versions
    arcpy.env.workspace = workspace + os.sep + iso + '.gdb'
    delTbls = arcpy.ListTables('*population_v*')
    for delTbl in delTbls:
        arcpy.Delete_management(delTbl)

print 'Script complete'
print datetime.datetime.now()-startTime
