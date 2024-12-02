import arcpy, os, datetime, multiprocessing, csv

def summarizeFishnets(gdb):
    startTime = datetime.datetime.now()
    iso = os.path.basename(gdb)[:3]
    rootName = os.path.basename(gdb)[:-12]
    arcpy.env.workspace = gdb
    fishnet = arcpy.ListFeatureClasses("*processed")[0]
    # create incremental variables
    WATERAREAKM=0
    AREAKMMASKED=0
    E_ATOTPOPBT_2010_CNTM = 0 
    with arcpy.da.SearchCursor(fishnet,"*") as rows:
        for row in rows:
            if not row[5]==None:
                WATERAREAKM+=row[5]
            if not row[6]==None:
                AREAKMMASKED+=row[6]
            if not row[11]==None:
                E_ATOTPOPBT_2010_CNTM+=row[11]
    return tuple([rootName,WATERAREAKM,AREAKMMASKED,E_ATOTPOPBT_2010_CNTM])
def main():
    scriptTime = datetime.datetime.now()
    # set workspaces and preprocess to attach paths
    inWS = r'F:\gpw\fishnets'
    #r'\\Dataserver0\gpw\GPW4\Release_4_0\Prod\Gridding\country\pop_tables'
    arcpy.env.workspace = inWS
    workspaces = arcpy.ListWorkspaces("*")
    workspaces.sort()
    gdb_list = []
    for workspace in workspaces:        
        # describe the workspace
        workDesc = arcpy.Describe(workspace)
        # if it is "BRA, CAN, GRL, RUS, or USA" then it is nested in subfolder
        if str(workDesc.workspaceType)=="FileSystem":
            if os.path.basename(workspace)=="can":
                continue
            workspace = workspace + os.sep + 'tiles'
            arcpy.env.workspace = workspace
            gdbs = arcpy.ListWorkspaces("rus*")
            for gdb in gdbs:
                gdb_list.append(gdb)
        else:
            gdb_list.append(workspace)
    header = tuple(["ISO","WATERAREKM","AREAKMMASKED","E_ATOTPOPBT_2010_CNTM"])
    print header
    tups = []
    for gdb in gdb_list:
##        print gdb
        tup = summarizeFishnets(gdb)
        tups.append(tup)
        print tup
    tot = 0
    for t in tups:
        tot+=t[3]
    print "Total pop 2010 = " + str(tot)
##    # multiprocess the data
##    pool = multiprocessing.Pool(processes=22,maxtasksperchild=1)
##    print pool.map(calculateGridCounts, gdb_list) 
##    # Synchronize the main process with the job processes to
##    # ensure proper cleanup.
##    pool.close()
##    pool.join()
    print "Script complete"
    print str(datetime.datetime.now()-scriptTime)

if __name__ == '__main__':
    main()
