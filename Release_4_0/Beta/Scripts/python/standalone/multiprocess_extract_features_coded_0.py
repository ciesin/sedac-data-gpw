# summarize count rasters
# Kytt MacManus
# create a summary table of count raster estimates

import arcpy, os, datetime, multiprocessing

def unAdjust(gdb):
    arcpy.env.overwriteOutput = True
    startTime = datetime.datetime.now()
    '''Create UN Adjustment Rasters'''
    outGDB = r'Z:\GPW4\Beta\Gridding\global\data_quality\features_coded_0'
    try:
        iso = os.path.basename(gdb)[:-4].upper()
        # set workspace
        arcpy.env.workspace = gdb
        # grab popFile
        popFile = arcpy.ListFeatureClasses("*boundaries_2010")[0]
        zeroLyr = iso + "_zeros"
        # make view
        expression = '"E_ATOTPOPBT_2010" = 0'
        if int(arcpy.GetCount_management(arcpy.MakeFeatureLayer_management(popFile,zeroLyr,expression))[0])==0:
            return iso + ": 0"
        else:
            outFile = outGDB + os.sep + os.path.basename(popFile) + ".shp"
            arcpy.CopyFeatures_management(zeroLyr,outFile)
            return iso + ": 1"
    except:
        return iso + " error: " + str(arcpy.GetMessages())
    

def main():
    scriptTime = datetime.datetime.now()
    # set workspaces and preprocess to attach paths
    workspace = r'Z:\GPW4\Beta\Gridding\country\features'
    arcpy.env.workspace = workspace
    workspaceFolders = arcpy.ListWorkspaces("egy*","Folder")
    folderGDBs = [os.path.join(ws, os.path.basename(ws)+".gdb") for ws in workspaceFolders]
    gdbs = arcpy.ListWorkspaces("egy*","FILEGDB")
    gdb_temp = [os.path.join(workspace, gdb) for gdb in gdbs]
    gdb_list = folderGDBs + gdb_temp
    gdb_list.sort()    
    print "processing"
    print len(gdb_list)
    # create multi-process pool and execute tool
    pool = multiprocessing.Pool(processes=30,maxtasksperchild=1)
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
