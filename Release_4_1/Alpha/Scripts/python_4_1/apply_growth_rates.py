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
    processTime = datetime.datetime.now()
    arcpy.env.overwriteOutput = True
    returnList = []
    arcpy.env.workspace = gdb
    iso = os.path.basename(gdb)[:-4]
    lookupTable = arcpy.ListTables("*lookup")[0]
    tableSplit = lookupTable.split("_")
    admin = tableSplit[1]
    adminYear = tableSplit[2]
    # get total_pop_input table
    popFile = iso + "_" + admin + "_" + adminYear + "_total"
    # check if the growth rate table exists
    if len(arcpy.ListTables('*growth_rate*'))==1:
        # temporary fix to update growth rate table
        agrFile = arcpy.ListTables('*growth_rate*')[0]
        arcpy.Delete_management(agrFile)
        arcpy.env.workspace = r'D:\gpw\release_4_1\loading\growth_rates.gdb'
        agrIn = arcpy.ListTables(iso + '*')[0]
        arcpy.CopyRows_management(agrIn,gdb+os.sep+os.path.basename(agrIn))
        arcpy.env.workspace = gdb
    else:
        return str(iso + " is missing an input growth rate table")
    # define the output estimatesTable and summaryTable
    inMemEstimates = "in_memory" + os.sep + iso + "_estimates"
    estimatesTable = popFile.replace("total","estimates")
    summaryTable = estimatesTable + "_summary"
    if arcpy.Exists(estimatesTable):
        arcpy.Delete_management(estimatesTable)
        arcpy.Delete_management(summaryTable)
        #return str(os.path.basename(gdb)) + " was already processed"

##    # read the agrTable into a dict
##    agrDict = {}
##    try:
##        with arcpy.da.SearchCursor(agrFile,["agrid","gr_start_year","gr_end_year","agr"]) as agrRows:
##            for agrRow in agrRows:
##                agrid = agrRow[0]
##                agrDict[agrid]=agrRow
##    except:
##        return [iso +  "problem with agr dict"]

    # create in memory estimates table
    arcpy.CopyRows_management(popFile,inMemEstimates)
    # join agr fields
    joinField = "AGRID"
    try:
        arcpy.JoinField_management(inMemEstimates,joinField,agrFile,"agrid",["agr","gr_start_year","gr_end_year"])
    except:
        return arcpy.GetMessages()
    # define target years
    targetYears = ["1975","1990","2000","2005","2010","2015","2020"]
    # iterate again
    for year in targetYears:
        # determine AGR exp by year - rpopyear
        yearTo = str(int(year) - int(adminYear))        
        # perform estimates. first project the total population to the reference year
        # add field to outTable
        try:
            eField = "E_ATOTPOPBT_" + year
            arcpy.AddField_management(inMemEstimates,eField,"DOUBLE")
        except:
            return arcpy.GetMessages()
        # construct calcExpression
        calcExpression = "!ATOTPOPBT! * math.exp( !agr! * " + yearTo + " )"
        # perform calculation
        try:
            arcpy.CalculateField_management(inMemEstimates,eField,calcExpression,"PYTHON_9.3")
            arcpy.AddMessage("Calculated " + eField)
        except:
            return arcpy.GetMessages()
    arcpy.CopyRows_management(inMemEstimates,estimatesTable)
    # finally summarize the atotpopbt and the estimates fields national
    summaryFields = [["gr_start_year","FIRST"],
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
    workspace = r'D:\gpw\release_4_1\loading\processed'
    arcpy.env.workspace = workspace
    print "processing"
    # must create procList
##    gdbs = arcpy.ListWorkspaces("*","FILEGDB")
    gdbs=arcpy.ListWorkspaces("blr*")
    procList = [os.path.join(workspace,gdb) for gdb in gdbs]
##    print procList[0]
    pool = multiprocessing.Pool(processes=1,maxtasksperchild=1)
    results = pool.map(applyGrowthRates, procList)
    for result in results:
        print result
##        for result2 in result:
####            if result2[0:9]=="Processed":
####                continue
##            print result2
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()
    print "Script Complete in " + str(datetime.datetime.now()-startTime)
if __name__ == '__main__':
    main()
