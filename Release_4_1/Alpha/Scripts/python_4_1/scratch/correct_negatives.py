# multiprocess template
import os, datetime
import multiprocessing
import arcpy
scriptTime = datetime.datetime.now()
def process(tbl):
    processTime = datetime.datetime.now()
    returnList = []
    iso = os.path.basename(tbl)[:3]
    admin = os.path.basename(tbl).split('_')[1]
    try:
        # grab the tables
        arcpy.env.workspace = r'D:\gpw\release_4_1\loading\processed' + os.sep + iso + '.gdb'
        tbls = arcpy.ListTables("*estimates")
        for t in tbls:
            tblView = t + "view"
            arcpy.MakeTableView_management(t, tblView,"ATOTPOPBT <0")
            if int(arcpy.GetCount_management(tblView)[0])>0:
                updateFields = ["ATOTPOPBT","UBID","POP_CONTEXT"]
                estimatesFields = [f.name for f in arcpy.ListFields(tblView,"E_*")]
                updateFields = updateFields + estimatesFields
                # update the table view
                with arcpy.da.UpdateCursor(tblView,updateFields) as rows:
                    for row in rows:
                        atotpopbt = row[0]
                        if row[2] is not None:
                            pass
                        elif int(atotpopbt)==-9999:
                            row[2]=111
                        elif int(atotpopbt)==-7777:
                            row[2]=115
                        elif int(atotpopbt)==-4444:
                            row[2]=113
                        elif int(atotpopbt)==-2222:
                            row[2]=108
                        else:
                            pass
                        i = 3
                        while i < len(estimatesFields)+3:
                            row[i]=0
                            i+=1
                        row[0]=0
                        rows.updateRow(row)
            summaryTable = t + "_summary"
            summaryFields = [["ISO","FIRST"],["ATOTPOPBT","SUM"]]
            summaryParams = arcpy.ListFields(t,"E_*")
            for summaryParam in summaryParams:
                summaryFields.append([summaryParam.name,"SUM"])
            arcpy.env.overwriteOutput=True
            arcpy.Statistics_analysis(t,summaryTable,summaryFields)
        returnList.append("Processed "+ iso + " " + str(datetime.datetime.now()-processTime))
    except:
        returnList.append("Error while processing " + iso + " " + str(datetime.datetime.now()-processTime))
    
    return returnList

def main():
    workspace = r'D:\gpw\release_4_1\loading\scratch\negatives.gdb'
    arcpy.env.workspace = workspace
    print "processing"
    # must create procList
    procList = [os.path.join(workspace,f) for f in arcpy.ListTables("can*")]
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





