# this script applies the proportions of a demographic to
# ATOTPOPBT to produce demographic estimates in year 2010

import arcpy, os, datetime, multiprocessing

def applyProportions(gdb):
    startTime = datetime.datetime.now()
    iso = os.path.basename(gdb)[:6]
    arcpy.env.workspace = gdb
    tbls = arcpy.ListTables("*")
    for tbl in tbls:
        print tbl
        if len(arcpy.ListFields(tbl,"USCID"))==1:
            arcpy.AddField_management(tbl,"UBID","TEXT")
            arcpy.CalculateField_management(tbl,"UBID","!USCID!","PYTHON")
            print "calculated ubid"
    

def main():
    scriptTime = datetime.datetime.now()
    # set workspaces and preprocess to attach paths
    inWS = r'H:\gpw\stage'
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
            workspace = workspace + os.sep + os.path.basename(workspace)+".gdb"
        gdb_list.append(workspace) 
    for gdb in gdb_list:
        print gdb
        print applyProportions(gdb)
##    # multiprocess the data
##    pool = multiprocessing.Pool(processes=5,maxtasksperchild=1)
##    print pool.map(applyProportions, gdb_list) 
##    # Synchronize the main process with the job processes to
##    # ensure proper cleanup.
##    pool.close()
##    pool.join()
    print "Script complete"
    print str(datetime.datetime.now()-scriptTime)

if __name__ == '__main__':
    main()
