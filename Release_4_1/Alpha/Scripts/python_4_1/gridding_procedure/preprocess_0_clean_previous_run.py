# Kytt MacManus
# December 2016

# Restructure the input raw country data into variable tables.

# import libraries globally 
import arcpy,datetime,os,sys,multiprocessing
scriptTime = datetime.datetime.now()
def process(gdb):
    arcpy.env.workspace = gdb
    rawTbls = arcpy.ListTables("*raw")
    if len(rawTbls)==0:
        return gdb + " does not have raw tables"
    lookupTbl = arcpy.ListTables("*lookup")
    growthRate = arcpy.ListTables("*growth_rate*")
    gdbName = os.path.basename(gdb)[:-4]
    outFolder = r'D:\gpw\release_4_1\loading\processed'
    outGDB = outFolder + os.sep + os.path.basename(gdb)
    if not arcpy.Exists(outGDB):
        arcpy.CreateFileGDB_management(outFolder,gdbName)
    tbls = rawTbls + lookupTbl + growthRate
    for tbl in tbls:
        arcpy.CopyRows_management(tbl,outGDB+os.sep+tbl)
    arcpy.Compact_management(outGDB)
    return "Cleaned " + gdb

    
def main():
    workspace = r'D:\gpw\release_4_1\input_data\pop_tables'
    arcpy.env.workspace = workspace
    # list tables
    gdbs = arcpy.ListWorkspaces("*")
    procList = [os.path.join(workspace,gdb) for gdb in gdbs]
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




