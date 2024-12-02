# summarize count rasters
# Kytt MacManus
# create a summary table of count raster estimates

import arcpy, os, datetime, multiprocessing

def unAdjust(gdb):
    startTime = datetime.datetime.now()
    
    try:
        iso = os.path.basename(gdb)[:3].upper()
        # set workspace
        arcpy.env.workspace = gdb
        # define unAdjTable
        unAdjTableIn = r'D:\gpw\ancillary.gdb\un_wpp2015_adjustment_factors_2_18_16'
        unAdjTable = 'in_memory' + os.sep + os.path.basename(unAdjTableIn) + "_" + iso
        arcpy.CopyRows_management(unAdjTableIn,unAdjTable)
        # grab adjustment factors from table
        # create dictionary to hold results
        adjFactors = {}
        with arcpy.da.SearchCursor(unAdjTable,["UNADJFAC_1975","UNADJFAC_1990",
                                               "UNADJFAC_2000","UNADJFAC_2005",
                                               "UNADJFAC_2010","UNADJFAC_2015",
                                               "UNADJFAC_2020"],'"'+"GPW4_ISO"+'" = ' + "'" +iso +"'") as rows:
            
            for row in rows:
                adjFactors[1975] = float(row[0])
                adjFactors[1990] = float(row[1])
                adjFactors[2000] = float(row[2])
                adjFactors[2005] = float(row[3])
                adjFactors[2010] = float(row[4])
                adjFactors[2015] = float(row[5])
                adjFactors[2020] = float(row[6])
        
        # grab estimates table
        table = arcpy.ListTables("*estimates")[0]
        # list estimates fields
        estimateFields = arcpy.ListFields(table,"E_*")
        for estimateField in estimateFields:
            name = estimateField.name
            year = name.split("_")[2]
            # get adjFactor
            adjFactor = adjFactors[int(year)]
            # add UNE field
            unField = "UN"+name
            arcpy.AddField_management(table,unField,"DOUBLE")
            try:
                arcpy.CalculateField_management(table,unField,"!"+name+"! +" + "!"+name+"! *" + str(adjFactor),"PYTHON")
            except:
                return arcpy.GetMessages()       
        
        # success
        return "Completed un adjustment for " + iso + ": " + str(datetime.datetime.now()-startTime)
    except:
        return iso + " error: " + str(arcpy.GetMessages())
    

def main():
    scriptTime = datetime.datetime.now()
    # set workspaces and preprocess to attach paths
    inWS = r'D:\gpw\stage\new_inputs\pop_tables'
    #r'\\Dataserver0\gpw\GPW4\Release_4_0\Prod\Gridding\country\pop_tables'
    arcpy.env.workspace = inWS
    workspaces = arcpy.ListWorkspaces("pol*")
    workspaces.sort()
    gdb_list = []
    for workspace in workspaces:
        print "processing " + os.path.basename(workspace)
        # describe the workspace
        workDesc = arcpy.Describe(workspace)
        # if it is "BRA, CAN, GRL, RUS, or USA" then it is nested in subfolder
        if str(workDesc.workspaceType)=="FileSystem":
            workspace = workspace + os.sep + os.path.basename(workspace)+".gdb"
        gdb_list.append(workspace) 
        print unAdjust(workspace)
    # multiprocess the data
##    pool = multiprocessing.Pool(processes=35,maxtasksperchild=1)
##    print pool.map(unAdjust, gdb_list) 
##    # Synchronize the main process with the job processes to
##    # ensure proper cleanup.
##    pool.close()
##    pool.join()
    print "Script complete"
    print str(datetime.datetime.now()-scriptTime)

if __name__ == '__main__':
    main()
