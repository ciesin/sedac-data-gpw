# multiprocess template
import os, datetime
import multiprocessing
import arcpy
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
    # create list of the tables to process
    tbls = arcpy.ListTables("*"+admin+"*"+year+"*")
    for tbl in tbls:
        if tbl == lookupTable:
            continue
        elif os.path.basename(tbl)[4:10]=='growth':
            continue
        elif tbl.split("_")[-1]=='raw':
            continue
        
        # read the lookupTable codes into memory
        lookupDict = {}
        try:
            with arcpy.da.SearchCursor(lookupTable,["USCID","UBID"]) as rows:
                for row in rows:
                    lookupDict[row[0]]=row
##            returnList.append(lookupDict.keys()[0:10])
##            return returnList
        except:
            returnList.append(str("Error reading lookup for " + iso))
            continue
        # create an in memory copy of tbl
        inMemTbl = 'in_memory' + os.sep + tbl
        arcpy.CopyRows_management(tbl,inMemTbl)
        # update the UBID
        try:
            with arcpy.da.UpdateCursor(inMemTbl,["USCID","UBID","POP_CONTEXT"]) as uRows:
                for uRow in uRows:
##                    returnList.append(uRow)
##                    return returnList
                    uscid = uRow[0]
                    if uscid not in lookupDict:
                        if uRow[2] is not None:
                            continue
                        else:        
                            returnList.append(str("Error in " + tbl + "  for " + str(uRow)))
                    else:
                        uRow[1]=lookupDict[uscid][1]
                    
                    uRows.updateRow(uRow)
    
        except:
            returnList.append(str("Error updating  " + tbl))
            continue
        # finally copy to disk
        arcpy.CopyRows_management(inMemTbl,os.path.join(gdb,tbl))
        returnList.append(str(str("Processed  " + tbl) + str(datetime.datetime.now()-processTime)))
    return returnList
 

def main():
    workspace = r'D:\gpw\release_4_1\loading\processed'
    arcpy.env.workspace = workspace
    print "processing"
    # must create procList
##    gdbs = arcpy.ListWorkspaces("*","FILEGDB")
    gdbs=arcpy.ListWorkspaces("uga*")
    procList = [os.path.join(workspace,gdb) for gdb in gdbs]
##    print procList[0]
    pool = multiprocessing.Pool(processes=1,maxtasksperchild=1)
    results = pool.map(process, procList)
    for result in results:
        for result2 in result:
##            if result2[0:9]=="Processed":
##                continue
            print result2
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()
    print "Script Complete in " + str(datetime.datetime.now()-scriptTime)
 
if __name__ == '__main__':
    main()
