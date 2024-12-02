# apply un adjustments
import os, datetime
import multiprocessing
import arcpy
scriptTime = datetime.datetime.now()
def process(gdb):
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
            summaryFields = [["ISO","FIRST"],["ATOTPOPBT","SUM"]]
            summaryParams = arcpy.ListFields(table,"*ATOTPOPBT*")
            for summaryParam in summaryParams:
                summaryFields.append([summaryParam.name,"SUM"])
            arcpy.env.overwriteOutput=True
            arcpy.Statistics_analysis(table,summaryTable,summaryFields)
        except:
            return (iso + ' error creating summary table')    

        returnList.append("Processed "+ iso + " " + str(datetime.datetime.now()-processTime))
    except:
        returnList.append("Error while processing " + iso + " " + str(datetime.datetime.now()-processTime))
    return returnList

def main():
    workspace = r'D:\gpw\release_4_1\loading\processed'
    arcpy.env.workspace = workspace
    print "processing"
    # must create procList
    workspaces = arcpy.ListWorkspaces("blr*",'FILEGDB')
    procList = [os.path.join(workspace,w) for w in workspaces]
    pool = multiprocessing.Pool(processes=1,maxtasksperchild=1)
    results = pool.map(process, procList)
    for result in results:
        print result
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()
    print "Script Complete in " + str(datetime.datetime.now()-scriptTime)
 
if __name__ == '__main__':
    main()
