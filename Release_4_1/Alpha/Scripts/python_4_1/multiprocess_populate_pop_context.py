# multiprocess template
import os, datetime
import multiprocessing
import arcpy
import csv
scriptTime = datetime.datetime.now()
def process(gdb):
    arcpy.env.overwriteOutput=True
    returnList = []
    # must specify
    processTime = datetime.datetime.now()
    iso = os.path.basename(gdb)[:-4]
    arcpy.env.workspace=gdb
    lookupTable = arcpy.ListTables("*lookup")[0]
    tableSplit = lookupTable.split("_")
    admin = tableSplit[1]
    year = tableSplit[2]
    rawTbl = arcpy.ListTables("*"+admin+"*"+year+"*raw")[0]
   
    # read the rawTable codes into memory
    rawDict = {}
    try:
        with arcpy.da.SearchCursor(rawTbl,["USCID","POP_CONTEXT"]) as rows:
            for row in rows:
                rawDict[row[0]]=row
##            return lookupDict.keys()
        hasPopContext = 1
        returnList.append((iso,1))
    except:
        returnList.append((iso,0))
        hasPopContext = 0
    tbls =  arcpy.ListTables("*"+admin+"*"+year+"*")
    for tbl in tbls:
        if tbl == lookupTable:
            continue
        elif tbl.split("_")[-1]=='raw':
            continue
        # check if the tbl has POP_CONTEXT, if not add it
        if len(arcpy.ListFields(tbl,"POP_CONTEXT"))==0:
               arcpy.AddField_management(tbl,"POP_CONTEXT","SHORT")

        if hasPopContext == 0:
            continue
        # create an in memory copy of tbl
        inMemTbl = 'in_memory' + os.sep + tbl
        arcpy.CopyRows_management(tbl,inMemTbl)
        # update the UBID
        try:
            with arcpy.da.UpdateCursor(inMemTbl,["USCID","POP_CONTEXT"]) as uRows:
                for uRow in uRows:
                    uscid = uRow[0]
                    if uscid not in rawDict:
                        continue
                        returnList.append(str("Error in " + iso + "  for " + str(uRow)))
                    else:
                        uRow[1]=rawDict[uscid][1]
                    uRows.updateRow(uRow)

        except:

            returnList.append(str("Error updating  " + tbl))
            
        # finally copy to disk
        arcpy.CopyRows_management(inMemTbl,os.path.join(gdb,tbl))
        returnList.append(str(str("Processed  " + tbl) + str(datetime.datetime.now()-processTime)))
    return returnList
 

def main():
    workspace = r'D:\gpw\release_4_1\loading\processed'
    arcpy.env.workspace = workspace
    print "processing"
    # open csvFile and write header
##    varFile = os.path.join(os.path.dirname(workspace),"pop_context_summary_01_12_17.csv")
##    varCSV = csv.writer(open(varFile,'wb'))
##    varCSV.writerow(('iso','has_pop_context'))
    # must create procList
    gdbs =arcpy.ListWorkspaces("usaaz*")
    procList = [os.path.join(workspace,gdb) for gdb in gdbs]
##    print procList[0]
    pool = multiprocessing.Pool(processes=1,maxtasksperchild=1)
    results = pool.map(process, procList)
    for result in results:
        for result2 in result:
##            if result2[1]==0:
##                varCSV.writerow(result2)
##            elif result2[1]==1:
##                varCSV.writerow(result2)
##            else:
            print result2
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()
##    del varCSV
    print "Script Complete in " + str(datetime.datetime.now()-scriptTime)
 
if __name__ == '__main__':
    main()
