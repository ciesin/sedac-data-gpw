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
    arcpy.CalculateField_management(lookupTable,"ISO","'"+iso.upper()+"'","PYTHON")
    
    tableSplit = lookupTable.split("_")
    admin = tableSplit[1]
    adminNum = int(admin[-1])
    year = tableSplit[2]
    rawTables = arcpy.ListTables("*raw")
    for rawTable in rawTables:
        # parse
        rawSplit = rawTable.split("_")
        rawAdmin = rawSplit[1]
        rawAdminNum = int(rawAdmin[-1])
        rawYear = rawSplit[2]
        # look for the next lowest admin level
        if rawAdminNum < adminNum:
            # then this is the table for all cases except irn, and swz
            if iso == 'irn':
                if rawAdminNum == 0:
                    break
                else:
                    continue
            elif iso == 'swz':
                if rawAdminNum == 1:
                    break
                else:
                    continue
            else:
                break
        else:
            continue

    if len(arcpy.ListFields(rawTable,"ISO"))==0:
        arcpy.AddField_management(rawTable,"ISO","TEXT")
    arcpy.CalculateField_management(rawTable,"ISO","'"+iso.upper()+"'","PYTHON")
    returnList.append("Calculated " + iso)
    return returnList
 

def main():
    workspace = r'D:\gpw\release_4_1\loading\processed'
    arcpy.env.workspace = workspace
    print "processing"
    # must create procList
##    gdbs = arcpy.ListWorkspaces("*","FILEGDB")
    gdbs=arcpy.ListWorkspaces("*","FILEGDB")
    procList = [os.path.join(workspace,gdb) for gdb in gdbs]
##    print procList[0]
    pool = multiprocessing.Pool(processes=10,maxtasksperchild=1)
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
