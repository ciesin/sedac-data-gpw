# apply growth rates
# GPW Beta
# 7-6-15
# Kytt MacManus

# import libraries
import arcpy, sys, os, datetime, imp
# import the checkForField, checkFieldType, and validateSchema functions to a module called custom
custom = imp.load_source('custom',r'\\Dataserver0\gpw\GPW4\Beta\Scripts\python\functions\validateSchema.py')
# set time counter
startTime = datetime.datetime.now()

# define agr table location
agrGDB = r'\\Dataserver0\gpw\GPW4\Beta\GrowthRate\country_tables_beta.gdb'

# define input country
iso = 'afg'
##iso = arcpy.GetParameterAsText(0)

# check if input table exists
inputRoot = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\country\inputs'
inputGDB = inputRoot + os.sep + iso + '.gdb'
arcpy.env.workspace = inputGDB
if len(arcpy.ListTables('*_input_population'))==1:
    inputTable = arcpy.ListTables('*_input_population')[0]
else:
    arcpy.AddMessage('Either the input_population table is missing or there are multiple versions. Correct and rerun')
    print 'Either the input_population table is missing or there are multiple versions. Correct and rerun'
    sys.exit()

# if the inputTable does exist, then check if the AGR table exists
agrTable = agrGDB + os.sep + iso.upper()
if not arcpy.Exists(agrTable):
    arcpy.AddMessage('The AGR table is missing, check and rerun')
    print 'The AGR table is missing, check and rerun'
    sys.exit()
# strip whitespace from all string fields in table
try:
    custom.stripWhiteSpace(agrTable)
except:
    print arcpy.GetMessages()

# create search cursor in order to determine agrid_source
searchCursor = arcpy.SearchCursor(agrTable)
searchCount = 0
searchRow = searchCursor.next()
while searchCount == 0:
    agrid_source = searchRow.getValue('agrid_source')
    searchCount = 1
del searchRow
del searchCursor

# parse agrid first
# need to handle complex agrid_source (e.g. UCADMIN1_UCADMIN2_UCADMIN3)
agridSplit = agrid_source.split('_')
for agridField in agridSplit:
    # check if this field exists in inputTable
    if custom.checkForField(inputTable,agridField)==0:
        arcpy.AddMessage(agridField + ' is missing from ' + inputTable + ' . Check and rerun')
        sys.exit()

# if the fields all exist, then create the estimates table
estimatesTable = inputTable.replace("input_population","estimates")
try:
    arcpy.CopyRows_management(inputTable,estimatesTable)
    arcpy.AddMessage('Created ' + estimatesTable)
except:
    print arcpy.GetMessages()
        
# parse agrid expression
if len(agridSplit)==1:
    agridExp = '!' + agridSplit[0] + '!'
else:
    agridFields = iter(agridSplit)
    next(agridFields)
    agridExp = '!' + agridSplit[0] + '!'
    for expField in agridFields:
        agridExp = agridExp + ' + ' + '"' + '_' + '" ' + '+ ' + '!' + expField + '!'
        
# create agrid in estimatesTable
try:
    arcpy.AddField_management(estimatesTable,'AGRID','TEXT')
    arcpy.CalculateField_management(estimatesTable,'AGRID',agridExp,"PYTHON")
except:
    print arcpy.GetMessages()

# validate AGRID join
joinField = "AGRID"
# if the join does not validate then rename the estimates table and end the script
if custom.validateJoin(estimatesTable,joinField,agrTable,joinField) == 0:
    estimatesError = estimatesTable + "_error"
    arcpy.Rename_management(estimatesTable,estimatesError)
    arcpy.AddMessage("The join didn't validate. Check AGRID and AGRID_SOURCE, are they correct?")
else:
    # create search cursor in order to determine rpopyear
    searchCursor = arcpy.SearchCursor(estimatesTable)
    searchCount = 0
    searchRow = searchCursor.next()
    while searchCount == 0:
        rpopyear = searchRow.getValue('RPOPYEAR')
        searchCount = 1
    del searchRow
    del searchCursor

    # join fields
    try:
        arcpy.JoinField_management(estimatesTable,joinField,agrTable,joinField,"agr")
    except:
        arcpy.GetMessages()
    # define target years
    targetYears = ["2000","2005","2010","2015","2020"]

    # iterate again
    for year in targetYears:
        # determine AGR exp by year - rpopyear
        yearTo = str(int(year) - int(rpopyear))
        arcpy.AddMessage("Generating estimates for year: " + year)
        # perform estimates. first project the total population to the reference year
        # add field to outTable
        try:
            eField = "E_ATOTPOPBT_" + year
            arcpy.AddField_management(estimatesTable,eField,"LONG")
        except:
            arcpy.GetMessages()
        # construct calcExpression
        calcExpression = "!ATOTPOPBT! * math.exp( !AGR! * " + yearTo + " )"
        # perform calculation
        try:
            arcpy.CalculateField_management(estimatesTable,eField,calcExpression,"PYTHON_9.3")
            arcpy.AddMessage("Calculated " + eField)
        except:
            arcpy.GetMessages()

    # finally summarize the atotpopbt and the estimates fields national
    summaryFields = [["RPOPYEAR","FIRST"],["ISO","FIRST"],
                     ["ATOTPOPBT","SUM"],["E_ATOTPOPBT_2000","SUM"],
                     ["E_ATOTPOPBT_2005","SUM"],["E_ATOTPOPBT_2010","SUM"],
                     ["E_ATOTPOPBT_2015","SUM"],["E_ATOTPOPBT_2020","SUM"]]
                     
    summaryTable = inputTable.replace("input_population","estimates_summary")
    try:
        arcpy.Statistics_analysis(estimatesTable,summaryTable,summaryFields)
        arcpy.AddMessage("Created " +  summaryTable)
    except:
        print arcpy.GetMessages()
print 'Script complete'
print datetime.datetime.now()-startTime
