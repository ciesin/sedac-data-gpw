# summarize count rasters
# Kytt MacManus
# create a summary table of count raster estimates

import arcpy, os, datetime, multiprocessing

def unAdjust(gdb):
    startTime = datetime.datetime.now()
    '''Create UN Adjustment Rasters'''
    
    try:
        iso = os.path.basename(gdb)[:-4].upper()
        # set workspace
        arcpy.env.workspace = gdb
        # define unAdjTable
        unAdjTableIn = r'\\dataserver0\gpw\GPW4\Beta\Gridding\ancillary.gdb\un_wpp2015_adjustment_factors'
        unAdjTable = 'in_memory' + os.sep + os.path.basename(unAdjTableIn)
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
        
        # create list of rasters to adjust
        rasters = arcpy.ListRasters("*ATOTPOPBT*")
        for raster in rasters:
            # parse year
            year = raster.split("_")[3]
            # get adjFactor
            adjFactor = adjFactors[int(year)]
            # check out spatial extension and do the calculation
            arcpy.CheckOutExtension("SPATIAL")
            arcpy.env.overwriteOutput = True
            outRaster = raster.replace("E_","UNE_")
            calc = arcpy.sa.Raster(raster)+ (arcpy.sa.Raster(raster) * adjFactor)
            calc.save(outRaster)      
        
        
        # success
        return "Created un adjusted rasters for " + iso + ": " + str(datetime.datetime.now()-startTime)
    except:
        return iso + " error: " + str(arcpy.GetMessages())
    

def main():
    scriptTime = datetime.datetime.now()
    # set workspaces and preprocess to attach paths
    workspace = r'F:\gpw\global\rasters'
    arcpy.env.workspace = workspace
    workspaceFolders = arcpy.ListWorkspaces("*","Folder")
    folderGDBs = [os.path.join(ws, os.path.basename(ws)+".gdb") for ws in workspaceFolders]
    gdbs = arcpy.ListWorkspaces("*","FILEGDB")
    gdb_temp = [os.path.join(workspace, gdb) for gdb in gdbs]
    gdb_list = folderGDBs + gdb_temp
    gdb_list.sort()    
    print "processing"
    print len(gdb_list)
    # create multi-process pool and execute tool
    pool = multiprocessing.Pool(processes=25,maxtasksperchild=1)
    results = pool.map(unAdjust, gdb_list)
    print(results)
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()
    print "Script complete"
    print str(datetime.datetime.now()-scriptTime)

if __name__ == '__main__':
    main()
