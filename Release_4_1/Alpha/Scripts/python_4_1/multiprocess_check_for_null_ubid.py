# multiprocess template
import os, datetime
import multiprocessing
import arcpy
scriptTime = datetime.datetime.now()
def process(gdb):
    # must specify
    processTime = datetime.datetime.now()
    iso = os.path.basename(gdb)[:-4]
    arcpy.env.workspace=gdb
    lookupTable = arcpy.ListTables("*lookup")[0]
    try:
        with arcpy.da.SearchCursor(lookupTable,"UBID") as rows:
            for row in rows:
                if row[0] is None:
                    return str(iso + " has a null UBID")
                elif row[0] == "":
                    return str(iso + " has a null UBID")
                else:
                    return str(str("Processed "+iso) + str(datetime.datetime.now()-processTime))
    except:
        return str(str("Error while processing " + iso) + str(datetime.datetime.now()-processTime))
    
 

def main():
    workspace = r'D:\gpw\release_4_1\loading\processed'
    arcpy.env.workspace = workspace
    print "processing"
    # must create procList
    gdbs = arcpy.ListWorkspaces("*","FILEGDB")
    procList = [os.path.join(workspace,gdb) for gdb in gdbs]
##    print procList[0]
    pool = multiprocessing.Pool(processes=20,maxtasksperchild=1)
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
