# multiprocess template
import os, datetime, socket
import multiprocessing
import arcpy
scriptTime = datetime.datetime.now()
def tableToDict(table,searchFields):
    values = {}
    # read the values
    with arcpy.da.SearchCursor(table,searchFields) as rows:
        for row in rows:
            # store with UBID as key and a tuple of numbers as value
            key = row[0]
            value = row
            values[key] = value
    return values
    
def process(outGDB):
    arcpy.env.overwriteOutput = True
    processTime = datetime.datetime.now()
    iso = os.path.basename(outGDB)[:3]
    rootName = os.path.basename(outGDB)[:-4]
    try:
        arcpy.env.workspace = outGDB
        inPop = arcpy.ListTables("*estimates")
        if len(inPop)==0:
            return outGDB + " estimates file is missing"
        else:
            estimatesFile = inPop[0]
        memFishnet = arcpy.ListTables("*intersect_estimates_table")
        if len(memFishnet)==0:
            return outGDB + " estimates file is missing"
        else:
            memFishnet = memFishnet[0]
        # create list of variables
        searchFields = ["UBID","MASKEDADMINAREA"]
        # read estimates into memory
        try:
            densities = tableToDict(estimatesFile,searchFields)
        except:
            return "Error in " + iso + ": Creating Estimates Dictionary"
        # write the density estimates to estimatesFile
        try:
            # read the values
            with arcpy.da.UpdateCursor(memFishnet,searchFields) as rows:
                for row in rows:                    
                    # grab the ubid
                    ubid = row[0]
                    if ubid in densities:
                        row[1] = densities[ubid][1]
                    else:
                        row[1] = 0
                    # update the row
                    rows.updateRow(row)
        except:
            return "Error in " + rootName + ": Writing Updates: " + str(row)
        
        # compact the file gdb to save space and improve performance
        arcpy.Compact_management(outGDB)
        return "Processed "+ outGDB + " " + str(datetime.datetime.now()-processTime)
    except:
        return "Error while processing " + outGDB + " " + str(datetime.datetime.now()-processTime) + " " + arcpy.GetMessages()
     

def main():
    host = socket.gethostname()
    if host == 'Devsedarc3':
        workspace = r'F:\gpw\release_4_1\process'
    elif host == 'Devsedarc4':
        workspace = r'D:\gpw\release_4_1\process'
    arcpy.env.workspace = workspace
    print "processing"
    procList = arcpy.ListWorkspaces("*")
    print procList
    # must create procList
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
