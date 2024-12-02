# copy necessary input files to country gridding fgdb
# produced for beta migration
# single country input
# kmacmanus
# 5-12-15
# added ability to work with multiple population tables, put input variables into ordered dictionaries,
# allow either excel or fgdb input tables, moved code into functions, 
# validations extended to ATOTPOPMT/FT fields, created pop_context functions and corresponding UBID validation,
# rewrote validation codes and errors, assigns negative census codes to pop_context, recode remaining negatives to 0
# logic to create VARID and validate join 
# jsquires
# 7-30-15

## REASONS TO FAIL VALIDATION
## IF VALIDATION FAILS THEN THE FINAL POP TABLE IS NOT WRITTEN
##1) USCID Duplicates
##2) The number of NAME fields does not match what was input for file name.
##3) ADMIN level does not match what was input
##4) The specified year value does not match the year value in the input table
##5) Negative values found in population field (ATOTPOPXX)
##6) Schema validation failure, missing field
##7) UBID Duplicates
##8) Invalid POP_CONTEXT code
##9) NULL UBID without POP_CONTEXT
##10) Variable table (VARID) does not join to total_pop_input (VARID) or vice-versa

# import libraries
import arcpy, sys, os, datetime, imp, time
from collections import OrderedDict as odict

# progressor function and total number of steps
arcpy.SetProgressor("default", "Let's validate some files!")

# import the checkForField, checkFieldType, and validateSchema functions to a module called custom
custom = imp.load_source('custom',r'\\Dataserver0\gpw\GPW4\Beta\Scripts\python\functions\validateSchema.py')
# import the print_and_log_msg from output-logger
log = imp.load_source('log',r'\\Dataserver0\gpw\GPW4\Beta\Scripts\python\functions\output-logger.py')

# set time counter
startTime = datetime.datetime.now()
        
# define gridding folder workspace
workspace = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\country\inputs'
arcpy.env.workspace = workspace

# define location of schema tables
schemas = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\schema_tables.gdb'

# set default for metadata variable
popContextExists = "N"

def add_and_calculate_text_field(table,field,fieldLength,expression):
    try:         
        arcpy.AddField_management(table,field,"TEXT","","",fieldLength)
        #arcpy.CalculateField_management(table,field,"{}".format(expression),"PYTHON")
        arcpy.CalculateField_management(table,field,expression,"PYTHON")
        return True
    except:
        add_msg_and_print( arcpy.GetMessages() )
        add_msg_and_print("Unable to add {} to {}".format(field,table))        
        return False
    
def add_msg_and_print(msg):
    '''
    prints message within Arc tool or stdout depending on whether runFromToolBox is True
    also logs message to logfile
    note: "logfile" variable, currently assigned outside of function
    '''
##    if runFromToolBox:
##        try:
##            arcpy.AddMessage(msg)
##        # because ArcGIS seems to get overwhelmed, at times when there are too many messages
##        except IOError:
##            pass
##    else:
##        print msg
    if runFromToolBox:
        try:
            arcpy.AddMessage(msg)
            log.print_and_log_msg(msg,logfile)
        # because ArcGIS seems to get overwhelmed, at times when there are too many messages
        except IOError:
            pass
    else:
        log.print_and_log_msg(msg,logfile)
    
def advance_progressor(message):
    if runFromToolBox:
        arcpy.SetProgressorLabel(message)
        arcpy.SetProgressorPosition()
    else:
        pass

def break_out():
    ''' for errors where we want to break out, report the error and create metadata ''' 
    write_diagnostics_table()
    write_metadata_table()
    arcpy.ResetProgressor()
    
def calculate_VARID_expression(idSource):
    '''
    idSource is a concatenated string of id field names
    returns an expression that will be used to calculate VARIDs
    '''
    # swap the delimiters and add exclamations and quotes at beginning and end
    varExp = '!'+idSource.replace('_','!+"_"+!')+'!'
    return varExp

def copy_fgdb_table(table, tableVariable):
    rawTable = "{}_{}_raw".format(rootName,tableVariable)
    try:
        arcpy.CopyRows_management(table,rawTable)
        add_msg_and_print('Copied ' + tableVariable + ' to ' + rawTable)
        return rawTable
    except:
        add_msg_and_print( arcpy.GetMessages() )
        add_msg_and_print("Failed to convert {} from FGDB".format(table))
        return False

def create_diagnostic_table(table, tableVariable):
    diagnosticTemplate = schemas + os.sep + "ingest_diagnostics"
    dTable = "{}_{}_diagnostics".format(rootName,tableVariable)
    try:
        arcpy.CopyRows_management(diagnosticTemplate,dTable)
        return dTable
    except:
        add_msg_and_print( arcpy.GetMessages() )

def create_table_from_excel(table, ingestTab, tableVariable):
    rawTable = "{}_{}_raw".format(rootName,tableVariable)
    try:
        arcpy.ExcelToTable_conversion(table,rawTable,ingestTab)
        add_msg_and_print('Copied ' + ingestTab + ' to ' + rawTable)
        return rawTable
    except:
        add_msg_and_print( arcpy.GetMessages() )
        add_msg_and_print("Failed to convert {} from Excel".format(table))
        return False

def create_varid_source(adminLevel):
    varSource = ""
    for i in range(int(adminLevel)+1):
        varSource += "UCADMIN{}_".format(i)
    return varSource[:-1]        
            
def overwrite_tables(tableWildCard):       
    arcpy.env.workspace = workspace + os.sep + iso + '.gdb'
    wildCard = "*{}*".format(tableWildCard)
    delTbls = arcpy.ListTables(wildCard)
    for delTbl in delTbls:
        try:
            message = "Deleting: {}".format(delTbl)
            add_msg_and_print(message)
            arcpy.Delete_management(delTbl)
        except:
            add_msg_and_print( arcpy.GetMessages() )
            failMessage = "Unable to delete {}. You may need to do this manually.".format(delTbl)
            add_msg_and_print(failMessage)
    arcpy.env.workspace = workspace

def process_duplicates(table, tableVariable, field):
    '''
    table: contains a table path with the data that will be checked for duplicates
    tableVariable: the type of data in the table, e.g. "sex" or "total_pop"
    field: the field in the table that will be checked for duplicates
    '''
    notNULLView = "{}_{}_{}_dupes".format(os.path.basename(rootName),tableVariable, field) 
    #notNULLExp = "{} IS NOT NULL OR CHAR_LENGTH({}) > 0".format(field, field)
#### NEED TO KNOW IF FIELD IS STRING OR NUMERIC IN ORDER TO FORM EXPRESSION
    if custom.checkFieldType(table,field,"String")==1:
        notNULLExp = "{} IS NOT NULL AND {} <> ''".format(field, field)
    else:
        notNULLExp = "{} IS NOT NULL".format(field)
    # first make a table view that excludes NULL and empty values
    arcpy.MakeTableView_management(table,notNULLView,notNULLExp)
    dupeView = "{}_{}_{}_duplicates_view".format(os.path.basename(rootName),tableVariable,field)
    # then check for duplicates
    if custom.checkForDuplicates(notNULLView,field,dupeView)==1:
    # if yes, then output the suspicious rows to a table
        try:
            duplicatesTable = "{}_{}_duplicate_{}s".format(rootName,tableVariable, field)
            arcpy.CopyRows_management(dupeView,duplicatesTable)
            add_msg_and_print("Created {}".format(duplicatesTable))
            validationReports.append((1,"Fix {} Duplicates".format(field),os.path.basename(duplicatesTable)))
        except:
            add_msg_and_print( arcpy.GetMessages() )

def write_diagnostics_table():
    global failCount
    # write validation reports to diagnostics table or validation success message
    advance_progressor("Writing Validation Reports")
    # create diagnosticTable to house validation reports
    diagnosticTable = create_diagnostic_table(table, description)
    # create insertCursor to add rows to diagnosticTable
    insertCursor = arcpy.da.InsertCursor(diagnosticTable,['PASS','DESCRIPTION','TABLE_LOC'])
    if len(validationReports)>0:
        # loop through the validationReports and write to diagnosticTable
        for validationReport in validationReports:
            if validationReport[0] > 0:
                failCount += 1;
            add_msg_and_print("Validation Report: " + str(validationReport))
            insertCursor.insertRow(validationReport)
    if failCount == 0:
        insertCursor.insertRow((0,"Validation successful, no errors found.",None))
        add_msg_and_print("Validation for {} found no issues.".format(description))
    del insertCursor
    arcpy.CalculateField_management(diagnosticTable,"ISO",'"' + str(iso.upper() + '"'),"PYTHON")

def write_metadata_table():
    # create processMetadata
    advance_progressor("Creating Metadata Table")
    processMetadataTemplate = schemas + os.sep + "process_metadata_1"
    processMetadataTable = "{}_{}_metadata".format(rootName,description)
    try:
        arcpy.CopyRows_management(processMetadataTemplate,processMetadataTable)
    except:
        add_msg_and_print( arcpy.GetMessages() )
    # populate the table with input parameters:
    # ObjectID,ISO,InputTable,InputFormat,ExcelTabName,AdminLevel,EstimateYear,LookupTable,LookupExcelTabName,PopContext,StartTime,EndTime
    metadataParams = (None,iso.upper(),tables[description],inputFormat,excelTabs[description],
                      admins[description],estimateYear,lookUpTable,lookUpTab,RowCountRaw,RowCountFinal,RowCountPopContext,
                      processStart.strftime("%Y-%m-%d %H:%M:%S"),datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    cursor = arcpy.da.InsertCursor(processMetadataTable,"*")
    cursor.insertRow(metadataParams)
    add_msg_and_print("Created metadata table: {}".format(processMetadataTable))
    # Delete cursor object
    del cursor

                             
#if running the script without the tool set runFromToolBox to False
runFromToolBox = False
    
if runFromToolBox:
    #request user input for parameters
    isoText = arcpy.GetParameterAsText(0)
    inputPopTable = arcpy.GetParameterAsText(1) or None
    ingestPopTab = arcpy.GetParameterAsText(2) or None
    ingestPopLevel = arcpy.GetParameterAsText(3) or None
    estimateYear = arcpy.GetParameterAsText(4)
    yearField = arcpy.GetParameterAsText(5)
    inputSexTable = arcpy.GetParameterAsText(6) or None
    ingestSexTab = arcpy.GetParameterAsText(7) or None
    ingestSexLevel = arcpy.GetParameterAsText(8) or None
    
    #Disabling Age and Urban/Rural functionality for now
    #renumber GetParameterAsText entries when reinstating
    ##inputAgeTable = arcpy.GetParameterAsText(9) or None
    ##ingestAgeTab = arcpy.GetParameterAsText(10) or None
    ##ingestAgeLevel = arcpy.GetParameterAsText(11) or None
    ##inputUrbanRuralTable = arcpy.GetParameterAsText(12) or None
    ##ingestUrbanRuralTab = arcpy.GetParameterAsText(13) or None
    ##ingestUrbanRuralLevel = arcpy.GetParameterAsText(14) or None
    inputAgeTable = None #currently turned off above
    ingestAgeTab = None #currently turned off above
    ingestAgeLevel = None  #currently turned off above
    inputUrbanRuralTable = None  #currently turned off above
    ingestUrbanRuralTab = None  #currently turned off above
    ingestUrbanRuralLevel = None  #currently turned off above
    
    lookUpTable = arcpy.GetParameterAsText(9) or None
    lookUpTab = arcpy.GetParameterAsText(10) or None
    overwriteTables = arcpy.GetParameter(11)
else:
    #set parameters here, for running outside of tool box and when runFromToolBox is set to False
    isoText = "BRN"
    inputPopTable = r'\\Dataserver0\gpw\GPW4\Beta\Preprocessing\Country\BRN\Ingest\Census\BRN_2011_ingest_admin2.xlsx'
    ingestPopTab = "brn_admin2_census_2011"
    ingestPopLevel = 2
    estimateYear = "2011"
    yearField = "CENSUS_YEAR"
    inputSexTable = r'\\Dataserver0\gpw\GPW4\Beta\Preprocessing\Country\BRN\Ingest\Census\BRN_2011_ingest_admin1.xlsx'
    ingestSexTab = "BRN_admin1_census_2011"
    ingestSexLevel = 1
    inputAgeTable = None
    ingestAgeTab = None
    ingestAgeLevel = None
    inputUrbanRuralTable = None
    ingestUrbanRuralTab = None
    ingestUrbanRuralLevel = None
    lookUpTable = r'\\Dataserver0\gpw\GPW4\Beta\Preprocessing\Country\BRN\Ingest\Census\BRN_2011_ingest_admin2.xlsx'
    lookUpTab = 'BRN_lookup_admin2'
    overwriteTables = True

iso = isoText.lower()

# define where logfile will be stored - this will be a copy of the output shown on the screen
logtime = time.strftime("%Y%m%d-%H%M%S") 
logfile = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\country\script_outputs' + os.sep + iso + logtime + ".txt"
# now initiliaze file
lf = open(logfile,'w')
lf.write("Validation logging for {} at {}\nInputs: {{{},{},{},{},{},{},{},{},{},{}}}\n".format(iso,logtime,isoText,inputPopTable,ingestPopLevel,
                                                                                                   estimateYear,yearField,inputSexTable,ingestSexLevel,
                                                                                                   lookUpTable,lookUpTab,overwriteTables))
lf.close()

# create ordered dictionaries for inputs
tables = odict([("total_pop",inputPopTable), ("sex_variables",inputSexTable), ("age_variables",inputAgeTable), ("urban_rural",inputUrbanRuralTable)])
excelTabs = odict([("total_pop",ingestPopTab), ("sex_variables",ingestSexTab), ("age_variables",ingestAgeTab), ("urban_rural",ingestUrbanRuralTab)])
admins = odict([("total_pop",ingestPopLevel), ("sex_variables",ingestSexLevel), ("age_variables",ingestAgeLevel), ("urban_rural",ingestUrbanRuralLevel)])

# reformat excelTabs input by looping over tab variable, location pairs
for tabVar, tabLoc in excelTabs.iteritems():
    if tabLoc is None:
        continue
    # we just want the name of the tab so remove the filepath an strp off any '$' characters
    tabName = os.path.basename(tabLoc).rstrip('$')
    excelTabs[tabVar] = tabName

# and dict for negative values that need to be recoded
negToPopContext = {-1111:111, -2222:108, -3333:112, -4444:113, -5555:114, -6666:109, -7777:115, -8888:116, -9999:111}

# clear in_memory workspace
arcpy.Delete_management("in_memory")

# create file geodatabase
isoGDB = workspace + os.sep + iso + '.gdb'
if not arcpy.Exists(isoGDB):
    try:
        arcpy.CreateFileGDB_management(workspace,iso)
        add_msg_and_print("\nCreated gridding file GDB")
    except:
        add_msg_and_print(arcpy.GetMessages())
else:
    add_msg_and_print("\nWARNING: The file GDB ({}.gdb) already exists. You may need to delete it or use the 'Overwrite' option.\n".format(iso))

# iterate through the 'tables' dictionary, where 'description' is the key and 'table' is the value
for description, table in tables.iteritems():

    validationReports = []
    failCount = 0
    RowCountFinal = None
    RowCountPopContext = None
    
    # skip tables that we are not processing this run
    if tables[description] is None:
        continue
    processStart = datetime.datetime.now()
    add_msg_and_print("\nValidating '{}' table: {}\n".format(description,table))
    arcpy.SetProgressor("step", "Validating '{}' table".format(description),0)
    time.sleep(2.5)

    # delete ingest and diagnostic tables from previous runs, if overwrite Boolean True
    advance_progressor("Preparing directories and tables.")
    if overwriteTables is True:
        overwrite_tables(description)
  
    # parse rootName
    rootName = workspace + os.sep + iso + '.gdb' + os.sep + iso + '_admin' + str(admins[description]) + '_' + str(estimateYear)

    # see if excel tab corresponding to table exists and convert to "gdb" table if necessary
    # if no excel tab was entered then, just use gdb table
    inputFormat = "FGDBT"
    if excelTabs[description] is None:    
        inRawTable = copy_fgdb_table(table, description)
        if inRawTable is False:
           validationReports.append((1,"Unable to copy FGDBT",table))
           break_out()
           break
    # else convert excel file    
    else:
        inputFormat = "Excel"
        inRawTable = create_table_from_excel(table, excelTabs[description], description)
        if inRawTable is False:
            validationReports.append((1,"Unable to create FGDBT from Excel: {}".format(excelTabs[description]),table))
            break_out()
            break
    RowCountRaw = int(arcpy.GetCount_management(inRawTable).getOutput(0)) 
    arcpy.AddMessage("Row: " + str(RowCountRaw))
    advance_progressor("Checking for duplicate USCIDs")
    process_duplicates(inRawTable,description,"USCID") 

    ##########check that adminLevel corresponds to the number of UCADMINS and NAMES########## 
    # are there the same number of UCADMIN fields as NAME fields?
    # if not, then validation fails
    advance_progressor("Processing UCADMINs")
    if not len(arcpy.ListFields(inRawTable,'NAME*'))==len(arcpy.ListFields(inRawTable,'UCADMIN*')):
        add_msg_and_print("Check table, the number of NAME columns does not match the number of UCADMIN fields")
        validationReports.append((1,"Number of NAME and UCADMIN columns do not match. Fix and rerun.",None))

    # check if the number of admin fields corresponds to what the user input for the adminLevel
    # define admin check as the number input by the user + 1 to account for admin0
    adminCheck = int(admins[description]) + 1
    if not len(arcpy.ListFields(inRawTable,'NAME*'))==adminCheck:
        add_msg_and_print("Check table, the number of NAME fields does not match what you input for the administrative level")
        validationReports.append((1,"Number of admin levels does not match what was input. Fix and rerun.",None))

    ##########check that estimateYear corresponds to the year captured in the data##########
    # check if the yearField is already in correct format and exists
    advance_progressor("Processing Year Fields")
    if custom.checkForField(inRawTable,yearField)==0:
        add_msg_and_print("The input yearField '{}' does not exist in the table. Fix and rerun".format(yearField))
        validationReports.append((1,"The input yearField '{}' does not exist in the table. Please fix and rerun".format(yearField),None))
        break_out()
        break
        
    # next run frequency analysis on the provided yearField in case it is not unique
    try:      
        yearTable = 'in_memory' + os.sep + iso + '_' + description + '_year'   
        arcpy.Frequency_analysis(inRawTable,yearTable,yearField)
        add_msg_and_print("Created {}".format(yearTable))
    except:
        add_msg_and_print( arcpy.GetMessages() )
        
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
    if not str(int(yearValue))==str(estimateYear):
        add_msg_and_print("Check table, the specified year value: {} does not match the year value in the input table: {}".format(estimateYear,int(yearValue)))
        validationReports.append((1,'Check table, the specified year value does not match the year value in the input table',None))                             

    # create a version of the input table which can be altered
    outPop1Tbl = "{}_{}_input_v01".format(rootName,description)
    try:
        arcpy.CopyRows_management(inRawTable,outPop1Tbl)
    except:
        add_msg_and_print( arcpy.GetMessages() )
    
    #########evaluate ATOTPOPXX field's for negative values and extract rows if needed##########
    ### NOTE - this iterates through a list of popFields, for ease of programming, as we started with just one field ATOTPOPBT
    ### would be more efficient to recode so that all popfields are looked at and handled in one pass
    if description == "total_pop":
        popFields = ["ATOTPOPBT"]
    else:
        popFields = ["ATOTPOPBT","ATOTPOPMT","ATOTPOPFT"]
    for popField in popFields:
        # check if table has popfield
        advance_progressor("Validating {} for negative values".format(popField))
        if custom.checkForField(outPop1Tbl,popField)==1:
            # first check outPop1Tbl to see if negative values need to be recoded as POP_CONTEXT
            negRecodeExp = "{} IN (-1111,-2222,-3333,-4444,-5555,-6666,-7777,-8888,-9999)".format(popField)    
            negRecodeView = "{}_{}_{}_recode_needed".format(os.path.basename(rootName),description,popField)
            if int(arcpy.GetCount_management(arcpy.MakeTableView_management(outPop1Tbl,negRecodeView,negRecodeExp))[0])>0:
                add_msg_and_print("Found negative codes to convert to POP_CONTEXT")
                # first make sure table has pop context, add if necessary
                if custom.checkForField(outPop1Tbl,'POP_CONTEXT')==0:
                    try:
                        arcpy.AddField_management(negRecodeView,'POP_CONTEXT','SHORT')
                        add_msg_and_print("Added POP_CONTEXT field to table")
                    except:
                        add_msg_and_print( arcpy.GetMessages() )
                # now recode the data
                fields = [popField,'POP_CONTEXT']
                with arcpy.da.UpdateCursor(negRecodeView,fields) as cursor:
                    for row in cursor:
                        # first use the dict to convert the negative code to pop_context
                        row[1] = negToPopContext[row[0]]
                        # then assign the negative value to 0
                        row[0] = 0
                        cursor.updateRow(row)
            # now check outPop1Tbl to see if there are any remaining NEGATIVE values
            negExp = "{} < 0".format(popField)
            negValueView = "{}_{}_{}_negs".format(os.path.basename(rootName),description,popField)
            if int(arcpy.GetCount_management(arcpy.MakeTableView_management(outPop1Tbl,negValueView,negExp))[0])>0:
                # if there are negative values, then extract them
                outNegTbl = "{}_{}_{}_negatives".format(rootName,description,popField.lower())              
                try:
                    # then create a table and report it
                    arcpy.CopyRows_management(negValueView,outNegTbl)
                    add_msg_and_print("Negative {} values found: {}".format(popField,outNegTbl))
                    validationReports.append((1,"Negative {} found and must be corrected".format(popField),os.path.basename(outNegTbl)))                 
                except:
                    add_msg_and_print( arcpy.GetMessages() )
                # next recode them as zeros
                try:
                    arcpy.CalculateField_management(negValueView,popField,0,"PYTHON_9.3")
                except:
                    add_msg_and_print( arcpy.GetMessages() )            
        else:
            add_msg_and_print("{} field is not present in {}".format(popField,inRawTable))
            validationReports.append((1,"{} Field is not present. Fix inputs".format(popField),None))

    # if ISO doesn't exist add ISO field and calculate it
    advance_progressor("Processing ISO Field")
    if custom.checkForField(outPop1Tbl,'ISO')==0:
        try:
            arcpy.AddField_management(outPop1Tbl,'ISO','TEXT','#','#',5)
            arcpy.CalculateField_management(outPop1Tbl,'ISO','"'+iso.upper()+'"','PYTHON')
            add_msg_and_print("Added and calculated ISO ({})".format( iso.upper() ))
        except:
            add_msg_and_print( arcpy.GetMessages() )
            
    # add and calculate RPOPYEAR as correct year name if needed
    advance_progressor("Processing RPOPYEAR")
    if custom.checkForField(outPop1Tbl,'RPOPYEAR')==0:
        try:
            arcpy.AddField_management(outPop1Tbl,'RPOPYEAR','SHORT')
            arcpy.CalculateField_management(outPop1Tbl,'RPOPYEAR','!'+yearField+'!','PYTHON')
            arcpy.DeleteField_management(outPop1Tbl,yearField)
            add_msg_and_print("Added and calculated RPOPYEAR")
        except:
            add_msg_and_print( arcpy.GetMessages() )

    # if we pass this check we can select the appropriate schema table and validate
    advance_progressor("Validating table against Schema")
    schemaTable = schemas + os.sep + description + '_admin' + str(admins[description])
    validationResults = custom.validateSchema(outPop1Tbl,schemaTable)
    # custom.validateSchema captures missing field names and incorrect field types
    uscidChange = False
    # if any of the variable tables are missing admins then we cannot validate the VARID join later
    variableMissingAdmins = False
    
    for validationResult in validationResults:
        # if the validation result fails based on type then transfer the data
        # to a field of the same name and type
        # validationResults in format (ValidationCode,FieldName,FieldType,ValidationDescription)
        if validationResult[0]==2:
            add_msg_and_print(validationResult)
            # if the USCID field changes type we need to know the type in order to properly join UBIDs later
            # uscidChange gets a value so is no longer "False"
            if (str(validationResult[1]) == "USCID" and description == "total_pop"):
                uscidChange = validationResult[2]
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
                add_msg_and_print("Corrected field type for: {}".format(validationField))
            except:
                add_msg_and_print( arcpy.GetMessages() )
        # if the validation fails based on a missing field name, then human intervention is needed
        # to decide if the field needs to be added or renamed
        elif validationResult[0]==3:
            # if the field in question is "POP_CONTEXT" then simply continue
            # the reason is that some tables may not have pop_context at the start, which is ok
            if validationResult[1]=="POP_CONTEXT":
                continue
            # if the field in question is a UCADMIN field from a variable table we cannot validate the VARID join later.
            if validationResult[1]=="UCADMIN*":
                if description != "total_pop":
                    variableMissingAdmins = True
            add_msg_and_print(validationResult)
            validationReports.append((1,"Schema validation failure, missing field: {}".format(validationResult[1]),None))
    
    # if the validations pass, then make a copy of the schema and load the data
    outPop2Tbl = "{}_{}_input_v02".format(rootName,description)
    try:
        arcpy.CopyRows_management(schemaTable,outPop2Tbl)
    except:
        add_msg_and_print( arcpy.GetMessages() )
    try:
        arcpy.Append_management(outPop1Tbl,outPop2Tbl,"NO_TEST")
        add_msg_and_print("Loaded: " + outPop2Tbl)


    except:
        add_msg_and_print(arcpy.GetMessages())
    
#############NEW CODE ADDED HERE TO TRY TO WORKAROUND APPEND ISSUE##############
    if int(arcpy.GetCount_management(outPop2Tbl).getOutput(0))==0:
        arcpy.Append_management(outPop1Tbl,outPop2Tbl,"NO_TEST")
        add_msg_and_print("There are still zero rows, the load won't work, so copy outPop1Tbl and delete the extra fields instead")
        try:
            arcpy.Delete_management(outPop2Tbl)
            arcpy.CopyRows_management(outPop1Table,outPop2Tbl)
        except:
            add_msg_and_print( arcpy.GetMessages() )
        # delete unneeded fields
        # create list of schema field names to check against
        schemaFldListObject = arcpy.ListFields(schemaTable,"*")
        schemaFldList = []
        for schemaFldObject in schemaFldListObject:
            schemaFldName = schemaFldObject.name
            schemaFldList.append(schemaFldName)
        # now check again outPop2Tbl
        pop2TblFldListObject = arcpy.ListFields(outPop2Tbl,"*")
        for pop2TblFldObject in pop2TblFldListObject:
            pop2TblFldName = pop2TblFldObject.name
            if not pop2TblFldName in schemaFldList:
                arcpy.DeleteField_management(outPop2Tbl,pop2TblFldName)
#############NEW CODE ADDED HERE TO TRY TO WORKAROUND APPEND ISSUE###############
    # the total_pop population must have a UBID joined
    # first need to update USCID in case it is the wrong type
    if description == "total_pop":
        advance_progressor("Checking if UBID needs joining")
        if uscidChange: 
            # if so add a temporary id, of the original type (uscidChange) and calculate
            try:
                arcpy.AddField_management(outPop2Tbl,"TMPID",uscidChange)
                arcpy.CalculateField_management(outPop2Tbl,"TMPID","!USCID!","PYTHON")
                arcpy.AddMessage("Calculated a USCID TMPID")
            except:
                add_msg_and_print( arcpy.GetMessages() )
            joinField = "TMPID"
        else:
            joinField = "USCID"
        
        ubidTable = ""
        # if it's in the raw table, get it from there
        if custom.checkForField(inRawTable,"UBID")==1:
            ubidTable = inRawTable
        # otherwise require a lookup table
        elif lookUpTable is None:
            add_msg_and_print("Lookup table is required to add UBID. Please address and rerun")
        else:
            # make a copy of the lookup table
            if lookUpTab is None:
                ubidTable = "{}_{}_lookup_raw".format(rootName,description)
                arcpy.Copy_management(lookUpTable,ubidTable)
            # or convert from excel if necessary    
            else:
                ubidTable = create_table_from_excel(lookUpTable, lookUpTab, "{}_lookup".format(description))

        # check to make sure there are no duplicate UBIDs in joinTable
        advance_progressor("Checking for duplicate UBIDs")
        process_duplicates(ubidTable,description,"UBID")

        # add UBID based on USCID join        
        try:
            arcpy.JoinField_management(outPop2Tbl,joinField,ubidTable,"USCID","UBID")
            add_msg_and_print("Joined UBID")
        except:
            add_msg_and_print( arcpy.GetMessages() )
        # delete TMPID if it was needed
        if uscidChange:
            try:
                arcpy.DeleteField_management(outPop2Tbl,"TMPID")
            except:
                add_msg_and_print( arcpy.GetMessages() )
             
    # check if POP_CONTEXT field has values and write contents to table
    advance_progressor("Checking for POP_CONTEXT field")
    popContextView = "{}_{}_popContext".format(os.path.basename(rootName),description)
    popContextTable = "{}_{}_pop_context".format(rootName,description)
    popContextExp = "POP_CONTEXT IS NOT NULL"
    if int(arcpy.GetCount_management(arcpy.MakeTableView_management(outPop2Tbl,popContextView,popContextExp))[0])>0:
        try:
            arcpy.CopyRows_management(popContextView,popContextTable)
            popContextExists = "Y"
            RowCountPopContext = int(arcpy.GetCount_management(popContextTable).getOutput(0)) 
            add_msg_and_print("POP_CONTEXT field found and written to table")
            # now make sure POP_CONTEXT is valid
            invalidPopContextView = "{}_{}_invalidPopContext".format(os.path.basename(rootName),description)
            invalidPopContextExp = "POP_CONTEXT NOT BETWEEN 101 AND 116"
            if int(arcpy.GetCount_management(arcpy.MakeTableView_management(popContextTable,invalidPopContextView,invalidPopContextExp))[0])>0:
                add_msg_and_print("Invalid POP_CONTEXT code found. Fix error.")
                validationReports.append((1,"Invalid POP_CONTEXT code found. Fix error.",os.path.basename(popContextTable)))
            else:
                validationReports.append((0,"POP_CONTEXT data found.",os.path.basename(popContextTable)))
        except:
            add_msg_and_print( arcpy.GetMessages() )
    else:
        RowCountPopContext = 0

    if description == "total_pop":        
        # check if there are any null UBIDs without POP_CONTEXT
        nullUBIDView = "{}_{}_nullUBIDS".format(os.path.basename(rootName),description)
        nullUBIDTbl = "{}_{}_null_UBIDs".format(rootName,description)
        nullExp = "UBID IS NULL AND (POP_CONTEXT IS NULL OR POP_CONTEXT NOT BETWEEN 101 AND 116)"
        if int(arcpy.GetCount_management(arcpy.MakeTableView_management(outPop2Tbl,nullUBIDView,nullExp))[0])>0: 
            # if yes then write them out
            try:
                arcpy.CopyRows_management(nullUBIDView,nullUBIDTbl)
            except:
                add_msg_and_print( arcpy.GetMessages() )
            add_msg_and_print("There are null UBIDs without POP_CONTEXT, Check and rerun")
            validationReports.append((1,"Null UBIDs found. Fix error or add POP_CONTEXT field",os.path.basename(nullUBIDTbl)))

    ####### for variable tables (sex,age, etc.) we need to add the VARID and VARID_SOURCE #######
    # then make sure the VARID can join to the total_pop_input table
    # VARID is created by the concatenating UCAMDIN fields

    varidSource = ""
    # first we determine the how the VARID is created by calculating and adding VARID_SOURCE
    # but we can't if UCADMIN fields were previously found missing
    if variableMissingAdmins:
        add_msg_and_print("Cannot create VARID because one of the required UCADMIN fields is missing")
        validationReports.append((0,"Cannot create VARID due to earlier 'missing UCADMIN field' error",None))
    elif description != "total_pop":
        advance_progressor("Checking VARID joins to total_pop_input table")
        # calculate VARID_SOURCE
        varidSource = create_varid_source(admins[description])
        varSourceExpression = "'{}'".format(varidSource)
        # add VARID_SOURCE to table      
        if add_and_calculate_text_field(outPop2Tbl,"VARID_SOURCE",62,varSourceExpression):
            add_msg_and_print("Added and calculated VARID_SOURCE in {}".format(outPop2Tbl))
            # calculate VARID from VARID_SOURCE
            varidExpression = calculate_VARID_expression(varidSource)
            # add VARID to table
            if add_and_calculate_text_field(outPop2Tbl,"VARID",62,varidExpression):
                add_msg_and_print("Added and calculated VARID in {}".format(outPop2Tbl))
                # now we want to make sure the VARID joins with the total_pop_input table
                # first we need to make sure that total_pop_input exists
                arcpy.env.workspace = isoGDB
                tbls = arcpy.ListTables("*total_pop_input*")
                if len(tbls) == 1:
                    # god help us if there's more than 1
                    # copy tot_pop_input to a temporary table so we can join VARID to it later
                    totPopTempTbl = "{}_{}_tp_input_v01t".format(rootName,description)
                    try:
                        arcpy.CopyRows_management(tbls[0],totPopTempTbl)
                    except:
                        add_msg_and_print( arcpy.GetMessages() )

                    # we also need a copy of the current variables table
                    outPop3Tbl = "{}_{}_input_v03".format(rootName,description)
                    try:
                        arcpy.CopyRows_management(outPop2Tbl,outPop3Tbl)
                    except:
                        add_msg_and_print( arcpy.GetMessages() )
                        
                    # add TP_VARID id to totPopTempTbl
                    if add_and_calculate_text_field(totPopTempTbl,"TP_VARID",62,varidExpression):
                        # make table view then join by VARID
                        joinVARIDtoTPView = "{}_{}_VARIDtoTPView".format(os.path.basename(rootName),description)                   
                        arcpy.MakeTableView_management(totPopTempTbl,joinVARIDtoTPView)
                        try:
                            arcpy.JoinField_management(joinVARIDtoTPView,"TP_VARID",outPop3Tbl,"VARID","VARID")
                            add_msg_and_print("Successfully joined VARID TO TP_VARID")
                        except:
                            add_msg_and_print(arcpy.GetMessages())
                            add_msg_and_print("Failed to join VARID TO TP_VARID")

                        # no join the other way around, first making a table view
                        joinTPtoVARIDView = "{}_{}_TPtoVARIDView".format(os.path.basename(rootName),description)
                        arcpy.MakeTableView_management(outPop3Tbl,joinTPtoVARIDView)
                        try:
                            arcpy.JoinField_management(joinTPtoVARIDView,"VARID",totPopTempTbl,"TP_VARID","TP_VARID")
                            add_msg_and_print("Successfully joined TP_VARID TO VARID")
                        except:
                            add_msg_and_print(arcpy.GetMessages())
                            add_msg_and_print("Failed to join TP_VARID TO VARID")
                            
                        # test if joins are missing
                        nullVARIDView = "{}_{}_nullVARIDView".format(os.path.basename(rootName),description)
                        nullVARIDExp = "VARID IS NULL"
                        nullTP_VARIDView = "{}_{}_nullTP_VARIDView".format(os.path.basename(rootName),description)
                        nullTP_VARIDExp = "TP_VARID IS NULL"
                        # check for NULLs in the VARID join to TP_VARID and create error table if necessary
                        if int(arcpy.GetCount_management(arcpy.MakeTableView_management(joinVARIDtoTPView,nullVARIDView,nullVARIDExp))[0])>0:
                            try:
                                nullVARIDTbl = "{}_{}_VARID_to_TP_join_errors".format(rootName,description)
                                arcpy.CopyRows_management(nullVARIDView,nullVARIDTbl)
                                add_msg_and_print("Found NULL VARID when joining to total_pop_input")
                                validationReports.append((1,"VARID does not map to total_pop_input. Needs correction.",os.path.basename(nullVARIDTbl)))
                            except:
                                add_msg_and_print(arcpy.GetMessages())
                         # check for NULLs in the TP_VARID join to VARID and create error table if necessary
                        if int (arcpy.GetCount_management(arcpy.MakeTableView_management(joinTPtoVARIDView,nullTP_VARIDView,nullTP_VARIDExp))[0])>0:                          
                            try:
                                nullTPVARIDTbl = "{}_{}_TP_to_VARID_join_errors".format(rootName,description)
                                arcpy.CopyRows_management(nullTP_VARIDView,nullTPVARIDTbl)
                                add_msg_and_print("Found NULL TP_VARID when joining to total_pop_input")
                                validationReports.append((1,"total_pop_input row(s) not mapping to VARID. Correct so variable estimates can be inherited.",os.path.basename(nullTPVARIDTbl)))
                            except:
                                add_msg_and_print(arcpy.GetMessages())
                        else:
                            add_msg_and_print("VARID joins are successful")
                    else:
                        add_msg_and_print("Failed to add TP_VARID to {}".format(totPopTempTbl))
                else:
                    add_msg_and_print("total_pop_input table not found, cannot validate VARID join")
                    validationReports.append((0,"total_pop_input table not found, cannot validate VARID join, may need to fix and rerun",None))
            else:
                add_msg_and_print("Unable to calculate VARID")
                validationReports.append((1,"Unable to calculate VARID",None))
        else:
            add_msg_and_print("Unable to calculate VARID_SOURCE")
            validationReports.append((1,"Unable to calculate VARID_SOURCE",None))

##    # check for null UBIDs and delete them
##    # null UBIDs with and without POP_CONTEXT were recorded earlier.
##    if description == "total_pop":
##        nullUBID2View = "{}_{}_nullUBIDS_PC".format(rootName,description)# save to disk instead
##        nullUBID2Exp = "UBID IS NULL OR UBID = ''"
##        if int(arcpy.GetCount_management(arcpy.MakeTableView_management(outPop2Tbl,nullUBID2View,nullUBID2Exp))[0])>0:
##            # if yes delete them, these rows will not be gridded
##            try:
##                arcpy.DeleteRows_management(nullUBID2View)
##                add_msg_and_print("Deleted NULL UBIDS from input table")
##            except:
##                add_msg_and_print( arcpy.GetMessages() )

    # note error if table is empty
    if int(arcpy.GetCount_management(outPop2Tbl).getOutput(0))==0:
        add_msg_and_print("Input table is empty!")
        validationReports.append((1,"Input table is empty. There must have been a problem.",None))        

    # write validatation reports to diagnostics table           
    write_diagnostics_table()       

    # if no failures found in diagnostics then create final table, else create a "FAIL" table
    if not failCount:
        outPopTable = "{}_{}_input".format(rootName,description)
    else:       
        outPopTable = "{}_{}_input_FAIL".format(rootName,description)
    advance_progressor("Creating final {} input table".format(description))
    try:
        arcpy.CopyRows_management(outPop2Tbl,outPopTable)
        add_msg_and_print("Created {}".format(outPopTable))
        RowCountFinal = int(arcpy.GetCount_management(outPopTable).getOutput(0)) 
    except:
        add_msg_and_print( arcpy.GetMessages() )
            
    # strip whitespace from all string fields in table
    try:
        custom.stripWhiteSpace(outPopTable)
    except:
        add_msg_and_print( arcpy.GetMessages() )

    # delete any temp input population versions
    advance_progressor("Cleaning up temp files")
    overwrite_tables("{}*_v0".format(description))

    # now create a metadata table
    write_metadata_table()    
    
    arcpy.ResetProgressor()

arcpy.SetProgressor("default", "Validation complete!")
time.sleep(2.5)
s = (datetime.datetime.now()-startTime).seconds
add_msg_and_print("Time to complete: {:0>2d}:{:0>2d}:{:0>2d}".format(s//3600, s%3600//60, s%60))


