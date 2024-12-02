import arcpy, os, multiprocessing, datetime
        
def compact(gdb):
    try:
        arcpy.Compact_management(gdb)
        return "Compacted " + os.path.basename(gdb)
    except:
        return "ERROR: " + os.paht.basename(gdb) + " " + str(arcpy.GetMessages())
        
    
def main():
    workspaces = [r'G:\gpw\admin0_fishnets']#usaSpace,tiledSpace
    # parse workspaces to make 1 master list
    gdb_list = []
    for ws in workspaces:
        arcpy.env.workspace = ws
        gdbs = arcpy.ListWorkspaces('*',"FILEGDB")
        gdbs.sort(reverse=False)
        gdb_temp = [os.path.join(ws, gdb) for gdb in gdbs]
        for gdbt in gdb_temp:
            gdb_list.append(gdbt)    
       
    print "processing"
    print len(gdb_list)
##    for gdb in gdb_list:
##        print gdb
##        joinCounts(gdb)
    # create multi-process pool and execute tool
    pool = multiprocessing.Pool(processes=4,maxtasksperchild=1)
    results = pool.map(compact, gdb_list)
    print(results)
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()
if __name__ == '__main__':
    main()















    
