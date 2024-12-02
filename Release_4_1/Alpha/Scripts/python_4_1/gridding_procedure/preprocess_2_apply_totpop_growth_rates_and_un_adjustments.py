# this script does the following
# create "estimates" table
# join growth rate information
# create estimates for target years
# summarize estimates
# 7-6-15
# Kytt MacManus

# import libraries
import arcpy, sys, os, datetime, multiprocessing
def applyUNAdjustments(gdb):
    processTime = datetime.datetime.now()
    returnList = []
    try:
        iso = os.path.basename(gdb)[:3].upper()
        unAdjTableIn = r'D:\gpw\ancillary.gdb\un_wpp2015_adjustment_factors_2_21_17'
        unAdjTable = 'in_memory' + os.sep + os.path.basename(unAdjTableIn) + "_" + iso
        arcpy.CopyRows_management(unAdjTableIn,unAdjTable)
        # grab adjustment factors from table
        # create dictionary to hold results
        adjFactors = {}
        try:
            with arcpy.da.SearchCursor(unAdjTable,["UNADJFAC_1975","UNADJFAC_1990",
                                                   "UNADJFAC_2000","UNADJFAC_2005",
                                                   "UNADJFAC_2010","UNADJFAC_2015",
                                                   "UNADJFAC_2020"],'"'+"GPW4_ISO"+'" = ' + "'" +iso +"'") as rows:
                
                for row in rows:
                    adjFactors[1975] = float(row[0])
                    adjFactors[1990] = float(row[1])
                    adjFactors[2000] = float(row[2])
                    adjFactors[2005] = float(row[3])
                    adjFactors[2010] = float(row[4])
                    adjFactors[2015] = float(row[5])
                    adjFactors[2020] = float(row[6])
        except:
            returnList.append(iso + ' error reading adjustment factors')
            return returnList
        # grab estimates table
        arcpy.env.workspace = gdb
        table = arcpy.ListTables("*estimates")[0]
        # list estimates fields
        estimateFields = arcpy.ListFields(table,"E_ATOTPOPBT*")
        for estimateField in estimateFields:
            name = estimateField.name
            year = name.split("_")[2]
            # get adjFactor
            adjFactor = adjFactors[int(year)]
            # add UNE field
            unField = "UN"+name
            arcpy.AddField_management(table,unField,"DOUBLE")
            try:
                arcpy.CalculateField_management(table,
                                                unField,"!"+name+"! +" + "!"+name+"! *" + str(adjFactor),
                                                "PYTHON")
            except:
                returnList.append("Error calculating " + unField)
                return returnList
        # finally summarize the atotpopbt and the estimates fields national
        try:
            summaryTable = table + "_total_pop_summary"
            summaryFields = [["ISO","FIRST"]]
            summaryParams = arcpy.ListFields(table,"*ATOTPOPBT*")
            for summaryParam in summaryParams:
                summaryFields.append([summaryParam.name,"SUM"])
            arcpy.env.overwriteOutput=True
            arcpy.Statistics_analysis(table,summaryTable,summaryFields)
        except:
            return (iso + ' error creating summary table')    

        returnList.append("applied un adjustments to "+ iso + " " + str(datetime.datetime.now()-processTime))
    except:
        returnList.append("Error while processing " + iso + " " + str(datetime.datetime.now()-processTime))
    return returnList
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
##    # check if the growth rate table exists
##    if len(arcpy.ListTables('*growth_rate*'))==1:
##        # temporary fix to update growth rate table
##        agrFile = arcpy.ListTables('*growth_rate*')[0]
##        arcpy.Delete_management(agrFile)
##        arcpy.env.workspace = r'D:\gpw\release_4_1\loading\growth_rates.gdb'
##        agrIn = arcpy.ListTables(iso + '*')[0]
##        arcpy.CopyRows_management(agrIn,gdb+os.sep+os.path.basename(agrIn))
##        arcpy.env.workspace = gdb
##    else:
##        return str(iso + " is missing an input growth rate table")
    agrFile = arcpy.ListTables('*growth_rate*')[0]
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

    return "applied growth rates to " + str(os.path.basename(gdb))

def main():
    # set time counter
    startTime = datetime.datetime.now()
    workspace = r'D:\gpw\release_4_1\loading\processed'
    arcpy.env.workspace = workspace
    print "processing"
    # must create procList
##    gdbs = arcpy.ListWorkspaces("*","FILEGDB")
    gdbs=arcpy.ListWorkspaces("cpv*")
    procList = [os.path.join(workspace,gdb) for gdb in gdbs]
##    print procList[0]
    pool = multiprocessing.Pool(processes=1,maxtasksperchild=1)
    results = pool.map(applyGrowthRates, procList)
    for result in results:
        print result
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()
    pool2 = multiprocessing.Pool(processes=1,maxtasksperchild=1)
    results2 = pool2.map(applyUNAdjustments, procList)
    for result2 in results2:
        print result2[0]
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool2.close()
    pool2.join()
    print "Script Complete in " + str(datetime.datetime.now()-startTime)
if __name__ == '__main__':
    main()
