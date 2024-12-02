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

### define input country
##iso = 'afg'
##iso = arcpy.GetParameterAsText(0)

workspace = r'\\dataserver0\gpw\GPW4\Beta\Gridding\country\inputs'
usaSpace = r'\\dataserver0\gpw\GPW4\Beta\Gridding\country\inputs\usa\tiles'
workspaces = [workspace]#,usaSpace]
gdb_list = []
for ws in workspaces:
    arcpy.env.workspace = ws
    gdbs = arcpy.ListWorkspaces('ecu*',"FILEGDB")
    gdbs.sort()
##    gdb_list.append(gdbs[0])
    gdb_temp = [os.path.join(ws, gdb) for gdb in gdbs]
    for gdbt in gdb_temp:
        gdb_list.append(gdbt)    

for inputGDB in gdb_list:
    print "processing " + inputGDB
    arcpy.env.workspace = inputGDB
    iso = os.path.basename(inputGDB)[:-4]
    if len(arcpy.ListTables('*_estimates'))==1:
        estimatesTable = inputGDB + os.sep + arcpy.ListTables('*_estimates')[0]
    else:
        arcpy.AddMessage('Either the input_population table is missing or there are multiple versions. Correct and rerun')
        print 'Either the input_population table is missing or there are multiple versions. Correct and rerun'
        sys.exit()
    summaryTable = estimatesTable + "_summary"
    # if summaryTable exists it is already processed
    if arcpy.Exists(summaryTable):
        print summaryTable + " already exists"
    else:
        # if the estimatesTable does exist, then check if the AGR table exists
        if os.path.dirname(inputGDB)==usaSpace:
            agrFile = agrGDB + os.sep + "USA_growth_rate_admin2_2000_2010"
            agrTable = inputGDB + os.sep + iso + "_growth_rate_admin2_2000_2010"
        else:
            arcpy.env.workspace = r'\\Dataserver0\gpw\GPW4\Beta\GrowthRate\country_tables_beta.gdb'
            agrFile = arcpy.ListTables(iso + "*")[0]
            agrTable = inputGDB + os.sep + os.path.basename(agrFile.lower())
        # copy the table into the country gdb        
        arcpy.CopyRows_management(agrFile,agrTable)
        
        # create search cursor in order to determine rpopyear
        searchCursor = arcpy.SearchCursor(estimatesTable)
        searchCount = 0
        searchRow = searchCursor.next()
        while searchCount == 0:
            rpopyear = searchRow.getValue('RPOPYEAR')
            searchCount = 1
        del searchRow
        del searchCursor

        # join agr fields
        joinField = "AGRID"
        try:
            arcpy.JoinField_management(estimatesTable,joinField,agrFile,"agrid",["agr","gr_start_year","gr_end_year"])
        except:
            print arcpy.GetMessages()
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
        summaryFields = [["RPOPYEAR","FIRST"],["gr_start_year","FIRST"],
                         ["gr_end_year","FIRST"],["ISO","FIRST"],
                         ["ATOTPOPBT","SUM"],["E_ATOTPOPBT_2000","SUM"],
                         ["E_ATOTPOPBT_2005","SUM"],["E_ATOTPOPBT_2010","SUM"],
                         ["E_ATOTPOPBT_2015","SUM"],["E_ATOTPOPBT_2020","SUM"]]
                         
        summaryTable = estimatesTable + "_summary"
        try:
            arcpy.Statistics_analysis(estimatesTable,summaryTable,summaryFields)
            arcpy.AddMessage("Created " +  summaryTable)
        except:
            print arcpy.GetMessages()
print 'Script complete'
print datetime.datetime.now()-startTime
