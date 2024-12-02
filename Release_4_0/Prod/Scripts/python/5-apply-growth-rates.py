# this script does the following
# create "estimates" table
# join growth rate information
# create estimates for target years
# summarize estimates
# 7-6-15
# Kytt MacManus

# import libraries
import arcpy, sys, os, datetime, multiprocessing

def applyGrowthRates(gdb):
    arcpy.env.overwriteOutput = True
    print "processing " + gdb
    arcpy.env.workspace = gdb
    iso = os.path.basename(gdb)[:-4]
    # get total_pop_input table
    popFile = arcpy.ListTables("*pop_input")[0]
    # check if the growth rate table exists
    if len(arcpy.ListTables('*growth_rate*'))==1:
        agrFile = arcpy.ListTables('*growth_rate*')[0]
    else:
        return str(iso + " is missing an input growth rate table")
    # define the output estimatesTable and summaryTable
    estimatesTable = popFile.replace("input","estimates")
    summaryTable = estimatesTable + "_summary"
    if arcpy.Exists(estimatesTable):
        return str(os.path.basename(gdb)) + " was already processed"
    # create estimates table
    arcpy.CopyRows_management(popFile,estimatesTable)
    # parse AGRID
    # create search cursor in order to determine agrid_source
    searchCursor = arcpy.SearchCursor(agrFile)
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
    # parse agrid expression
    if len(agridSplit)==1:
        agridExp = '!' + agridSplit[0] + '!'
    else:
        agridFields = iter(agridSplit)
        next(agridFields)
        agridExp = '!' + agridSplit[0] + '!'
        for expField in agridFields:
            agridExp = agridExp + ' + ' + '"' + '_' + '" ' + '+ ' + '!' + expField + '!'
    # add and calculate agrid
    arcpy.AddField_management(estimatesTable,"AGRID","TEXT","","",200)
    arcpy.CalculateField_management(estimatesTable, "AGRID", agridExp,"PYTHON")    
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
        return arcpy.GetMessages()
    # define target years
    targetYears = ["1975","1990","2000","2005","2010","2015","2020"]
    # iterate again
    for year in targetYears:
        # determine AGR exp by year - rpopyear
        yearTo = str(int(year) - int(rpopyear))        
        # perform estimates. first project the total population to the reference year
        # add field to outTable
        try:
            eField = "E_ATOTPOPBT_" + year
            arcpy.AddField_management(estimatesTable,eField,"DOUBLE")
        except:
            return arcpy.GetMessages()
        # construct calcExpression
        calcExpression = "!ATOTPOPBT! * math.exp( !agr! * " + yearTo + " )"
        # perform calculation
        try:
            arcpy.CalculateField_management(estimatesTable,eField,calcExpression,"PYTHON_9.3")
            arcpy.AddMessage("Calculated " + eField)
        except:
            return arcpy.GetMessages()

    # finally summarize the atotpopbt and the estimates fields national
    summaryFields = [["RPOPYEAR","FIRST"],["gr_start_year","FIRST"],
                     ["gr_end_year","FIRST"],["ISO","FIRST"],
                     ["ATOTPOPBT","SUM"],["E_ATOTPOPBT_1975","SUM"],
                     ["E_ATOTPOPBT_1990","SUM"],["E_ATOTPOPBT_2000","SUM"],
                     ["E_ATOTPOPBT_2005","SUM"],["E_ATOTPOPBT_2010","SUM"],
                     ["E_ATOTPOPBT_2015","SUM"],["E_ATOTPOPBT_2020","SUM"]]
    try:
        arcpy.Statistics_analysis(estimatesTable,summaryTable,summaryFields)
    except:
        return arcpy.GetMessages()

    return "processed " + str(os.path.basename(gdb))

def main():
    # set time counter
    startTime = datetime.datetime.now()
    inWS = r'D:\gpw\stage\new_inputs\pop_tables'#r'F:\gpw\pop_tables'
    #r'\\Dataserver0\gpw\GPW4\Release_4_0\Prod\Gridding\country\pop_tables'
    arcpy.env.workspace = inWS
    workspaces = arcpy.ListWorkspaces("pol*")
    workspaces.sort()
    gdb_list = []
    for workspace in workspaces:
##        print "processing " + os.path.basename(workspace)
        # describe the workspace
        workDesc = arcpy.Describe(workspace)
        # if it is "BRA, CAN, GRL, RUS, or USA" then it is nested in subfolder
        if str(workDesc.workspaceType)=="FileSystem":
            workspace = workspace + os.sep + os.path.basename(workspace)+".gdb"
        gdb_list.append(workspace) 
        #print applyGrowthRates(workspace)
    # multiprocess the data
    pool = multiprocessing.Pool(processes=35,maxtasksperchild=1)
    print pool.map(applyGrowthRates, gdb_list) 
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()
    
    
    print 'Script complete'
    print datetime.datetime.now()-startTime
if __name__ == '__main__':
    main()
