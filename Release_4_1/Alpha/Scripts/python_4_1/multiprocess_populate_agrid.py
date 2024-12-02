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
    grWorkspace = r'D:\gpw\release_4_1\loading\growth_rates.gdb'
    arcpy.env.workspace = grWorkspace
    agrTableIn = arcpy.ListTables(iso[:3]+"*")[0]
    agrTable = os.path.join(gdb,agrTableIn)
##    if not arcpy.Exists(agrTable):
    arcpy.CopyRows_management(agrTableIn,agrTable)
    # change the workspace to gdb and grab lookup and total tables
    arcpy.env.workspace=gdb
    lookupTable = arcpy.ListTables("*lookup")[0]
    tableSplit = lookupTable.split("_")
    admin = tableSplit[1]
    year = tableSplit[2]
    totalTable = iso + "_"+admin+"_"+year+"_total"
##    return lookupTable, totalTable
    # read agrTable into memory 
    agrDict = {}
    agridSourceList=[]    
    try:
        with arcpy.da.SearchCursor(agrTable,["agrid","agrid_source","agr"]) as agrRows:
            for agrRow in agrRows:
                agridSource = agrRow[1]
                agridSourceList.append(agridSource)
                try:
                    agrDict[agrRow[0].strip()]=agrRow
                except:
                    agrDict[agrRow[0]]=agrRow
##        returnList.append("read " + agrTableIn)
    except:
        returnList.append("could not read " + agrTable)
        return returnList
    agridSourceSet=set(agridSourceList)
    lookupDict = {}
    for agridSource in agridSourceSet:
        searchList = ["USCID"]
        srcSplit = agridSource.split("_")
        # determine the semantics of agridSource
        for src in srcSplit:
            if src == "USCID":
                continue
            searchList.append(src)
        # read the lookupTable codes into memory
        try:
            with arcpy.da.SearchCursor(lookupTable,searchList) as lRows:
                for lRow in lRows:
                    if len(lRow)==1:
                        # then there is only USCID
                        try:
                            agridValue=lRow[0].strip()
                        except:
                            agridValue=lRow[0]
                    elif len(lRow)==2:
                        # then there is only USCID and one AGRID field
                        try:
                            agridValue=lRow[1].strip()
                        except:
                            agridValue=lRow[1]
                    else:
                        # otherwise there are multiple agrid fields to calculate
                        agridValue = ""
                        i = 1
                        for value in lRow:
                            if value == lRow[0]:
                                continue
                            elif agridValue=="":
                                try:
                                    agridValue=str(lRow[i]).strip()
                                except:
                                    agridValue=str(lRow[i])
                                i+=1
                            else:
                                try:
                                    agridValue = agridValue + "_" + str(lRow[i]).strip()
                                except:
                                    agridValue = agridValue + "_" + str(lRow[i])
                                i+=1
                    # only add it to the lookupDict if it is in agrDict
                    # this subsets to only the codes present in agrDict
##                    return (agridValue, agrDict)
                    if agridValue in agrDict:
                        try:
                            lookupDict[lRow[0].strip()]=agridValue
                        except:
                            lookupDict[lRow[0]]=agridValue
                    elif int(agridValue) in agrDict:
                        try:
                            lookupDict[lRow[0].strip()]=int(agridValue)
                        except:
                            lookupDict[lRow[0]]=int(agridValue)
                    else:
                        return [agridValue]#, agrDict)
        except:
            returnList.append(agridValue)
            returnList.append("could not write to dictionary: " + lookupTable)
            return returnList       
                    
##    return lookupDict
    # create an in memory copy of lookup Table and total Table
    # the update them

    updateTables = [lookupTable, totalTable]
    for tbl in updateTables:
        inMemTbl = 'in_memory' + os.sep + os.path.basename(tbl)
        arcpy.CopyRows_management(tbl,inMemTbl)
        # update the UBID
        try:
            updateCounter = 0
            rowCounter = 0
            with arcpy.da.UpdateCursor(inMemTbl,["USCID","AGRID"]) as uRows:
                for uRow in uRows:
                    rowCounter+=1
                    initialRow = uRow  
                    try:     
                        uscid = uRow[0]
                        if uscid not in lookupDict and uscid.strip() not in lookupDict:
##                            returnList.append(uscid)
##                            return returnList
                            continue 
                        else:
                            if uscid in lookupDict:
                                uRow[1]=lookupDict[uscid]
                            elif uscid.strip() in lookupDict:
                                uRow[1]=lookupDict[uscid.strip()]
##                        if uRow[1] == initialRow[1]:
##                            return 1
##                            continue
                        try:
                            uRows.updateRow(uRow)
                            updateCounter+=1
                        except:
                            return tbl, uRow
                    except:
                        return lookupDict[uscid.strip()]

        except:
            returnList.append(str("Error updating  " + tbl))
            return returnList
        # finally copy to disk
        arcpy.CopyRows_management(inMemTbl,os.path.join(gdb,tbl))
        if updateCounter == 0:
            returnList.append(str("Major Match Error  " + tbl + " for  " + str(updateCounter) + " out of " + str(rowCounter) + "  rows. Completed in " + str(datetime.datetime.now()-processTime)))
        elif updateCounter < rowCounter:
            returnList.append(str("Inconsistent result for  " + tbl + " for  " + str(updateCounter) + " out of " + str(rowCounter) + "  rows. Completed in " + str(datetime.datetime.now()-processTime)))
        else:
            returnList.append(str("Processed  " + tbl + " for  " + str(updateCounter) + " out of " + str(rowCounter) + "  rows. Completed in " + str(datetime.datetime.now()-processTime)))
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
    gdbs = arcpy.ListWorkspaces("bra*")+arcpy.ListWorkspaces("btn*")+arcpy.ListWorkspaces("can*")+arcpy.ListWorkspaces("cod*")+arcpy.ListWorkspaces("esh*")+arcpy.ListWorkspaces("flk*")+arcpy.ListWorkspaces("ggy*")+arcpy.ListWorkspaces("ind*")+arcpy.ListWorkspaces("irq*")+arcpy.ListWorkspaces("mex*")+arcpy.ListWorkspaces("mus*")+arcpy.ListWorkspaces("nzl*")+arcpy.ListWorkspaces("phl*")+arcpy.ListWorkspaces("svk*")+arcpy.ListWorkspaces("ury*")+arcpy.ListWorkspaces("vcs*")
    procList = [os.path.join(workspace,gdb) for gdb in gdbs]
    print procList
    pool = multiprocessing.Pool(processes=16,maxtasksperchild=1)
    results = pool.map(process, procList)
    for result in results:
        print result
        for result2 in result:
            if result2[0:9]=="Processed":
                continue
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
