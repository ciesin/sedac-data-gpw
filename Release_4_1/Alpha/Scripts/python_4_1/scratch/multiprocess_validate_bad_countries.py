# multiprocess template
import os, datetime
import multiprocessing
import arcpy
scriptTime = datetime.datetime.now()
def process(gdb):
    arcpy.env.overwriteOutput = True
    processTime = datetime.datetime.now()
    returnList = []
    try:
        outFolder = r'D:\gpw\release_4_1\validate'
        outGDB = outFolder + os.sep + os.path.basename(gdb)
        summaryTable = outGDB + os.sep + os.path.basename(gdb)[:-4] + "_summary"
        return [summaryTable]
        arcpy.CreateFileGDB_management(outFolder,os.path.basename(gdb)[:-4])
        arcpy.env.workspace = gdb
        estimatesTable = arcpy.ListTables("*estimates_table")[0]
        inEstimates = arcpy.ListTables("*estimates")[0]
##        return (estimatesTable,summaryTable)
        arcpy.Statistics_analysis(estimatesTable, summaryTable,
                                  [["ADMINAREA", "MAX"],["WATERAREA","MAX"],["MASKEDAREA", "MAX"],["PIXELAREA", "SUM"],
                                   ["AREAKM", "SUM"],["WATERAREAKM", "SUM"],["AREAKMMASKED", "SUM"],["E_ATOTPOPBT_2010_CNTM", "SUM"]],
                                  "UBID")
        arcpy.AddField_management(summaryTable,"INPUTPOP","DOUBLE")
        arcpy.AddField_management(summaryTable,"POPDIFF","DOUBLE")
        # read estimates in
        estimatesDict = {}
        with arcpy.da.SearchCursor(inEstimates,['UBID','E_ATOTPOPBT_2010']) as rows:
            for row in rows:
                estimatesDict[row[0]]=row[1]
        # update
        with arcpy.da.UpdateCursor(summaryTable,['UBID','SUM_E_ATOTPOPBT_2010_CNTM','INPUTPOP','POPDIFF']) as uRows:
            for uRow in uRows:
                ubid = uRow[0]
                inPop = uRow[1]
                if ubid in estimatesDict:
                    uRow[2] = estimatesDict[ubid]
                else:
                    uRow[2] = 0
                uRow[3] = uRow[2] - inPop
                uRows.updateRow(uRow)
        returnList.append(summaryTable)
        
    except:
        returnList.append("Error while processing " + gdb + " " + str(datetime.datetime.now()-processTime) + " " + arcpy.GetMessages())
    return returnList

def main():
    print "processing"
    # must create procList
    procList = [r"D:\gpw\release_4_1\process\are.gdb",
                r"D:\gpw\release_4_1\process\arg.gdb",
                r"D:\gpw\release_4_1\process\bra.gdb",
                r"D:\gpw\release_4_1\process\bwa.gdb",
                r"D:\gpw\release_4_1\process\chl.gdb",
                r"D:\gpw\release_4_1\process\chn.gdb",
                r"D:\gpw\release_4_1\process\cyp.gdb",
                r"D:\gpw\release_4_1\process\dza.gdb",
                r"D:\gpw\release_4_1\process\ggy.gdb",
                r"D:\gpw\release_4_1\process\idn.gdb",
                r"D:\gpw\release_4_1\process\irn.gdb",
                r"D:\gpw\release_4_1\process\kaz.gdb",
                r"D:\gpw\release_4_1\process\lao.gdb",
                r"D:\gpw\release_4_1\process\lby.gdb",
                r"D:\gpw\release_4_1\process\ltu.gdb",
                r"D:\gpw\release_4_1\process\mar.gdb",
                r"D:\gpw\release_4_1\process\mrt.gdb",
                r"D:\gpw\release_4_1\process\nzl.gdb",
                r"D:\gpw\release_4_1\process\phl.gdb",
                r"D:\gpw\release_4_1\process\pse.gdb",
                r"D:\gpw\release_4_1\process\sau.gdb",
                r"D:\gpw\release_4_1\process\sdn.gdb",
                r"D:\gpw\release_4_1\process\som.gdb",
                r"D:\gpw\release_4_1\process\ssd.gdb",
                r"D:\gpw\release_4_1\process\syr.gdb",
                r"D:\gpw\release_4_1\process\tcd.gdb",
                r"D:\gpw\release_4_1\process\tkm.gdb",
                r"D:\gpw\release_4_1\process\tur.gdb",
                r"D:\gpw\release_4_1\process\uga.gdb",
                r"D:\gpw\release_4_1\process\ukr.gdb",
                r"D:\gpw\release_4_1\process\uzb.gdb",
                r"D:\gpw\release_4_1\process\ven.gdb",
                r"D:\gpw\release_4_1\process\bol.gdb",
                r"D:\gpw\release_4_1\process\mli.gdb",
                r"D:\gpw\release_4_1\process\png.gdb",
                r"D:\gpw\release_4_1\process\ind.gdb",
                r"D:\gpw\release_4_1\process\fra.gdb",
                r"D:\gpw\release_4_1\process\ner.gdb",
                r"D:\gpw\release_4_1\process\irq.gdb"]
    pool = multiprocessing.Pool(processes=20,maxtasksperchild=1)
    results = pool.map(process, procList)
    vGDB = r'D:\gpw\release_4_1\validate\validate.gdb'
    if not arcpy.Exists(vGDB):
        arcpy.CreateFileGDB_management(r'D:\gpw\release_4_1\validate','validate')
    for result in results:
        tbl = result[0]
        if tbl[:5]=="Error":
            print tbl
            continue
        arcpy.CopyRows_management(tbl,vGDB + os.sep + os.path.basename(tbl))
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()
    print "Script Complete in " + str(datetime.datetime.now()-scriptTime)
 
if __name__ == '__main__':
    main()
