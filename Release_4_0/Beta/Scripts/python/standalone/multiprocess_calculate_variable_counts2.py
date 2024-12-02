import arcpy, os, multiprocessing, os
        
def calcCounts(gdb):
    arcpy.env.scratchWorkspace = "in_memory"
    # define inputs
    gdbName = os.path.basename(gdb)
    rootName = os.path.basename(gdb).replace("_fishnet.gdb","")
    fishnet = gdb + os.sep + rootName + "_fishnet_intersect"
    sumTable = gdb + os.sep + rootName + "_count_summary"
    if not arcpy.Exists(fishnet):
        return fishnet + " is missing"
    if arcpy.Exists(sumTable):
        return sumTable + " already exists"
    if len(arcpy.ListFields(fishnet,"*CNTM"))>0:
        return fishnet + " already has CNTM fields"
    
        
##    # create tmp dir
##    newTempDir = r"F:\gpwout\temp" + os.sep + rootName
##    if not arcpy.Exists(newTempDir):
##        os.mkdir(newTempDir)
##    os.environ["TEMP"] = newTempDir
##    os.environ["TMP"] = newTempDir
##    scratchGDB = newTempDir + os.sep + rootName + ".gdb"
##    if not arcpy.Exists(scratchGDB):
##        arcpy.CreateFileGDB_management(newTempDir,rootName)
    try:
        # create list of sumFields for calculating statistics
        sumFields = [['AREAKM','SUM'],['WATERAREAKM','SUM'],['AREAKMMASKED','SUM']]
        # list dsm fields and calculate cntm
        dsmFields = arcpy.ListFields(fishnet,"*DSM")
        for dsmField in dsmFields:
            cntField = str(dsmField.name).replace("DSM","CNTM")
            # add to sumFields
            sumFields.append([cntField,'SUM'])
            # add cntField to fishnet
            arcpy.AddField_management(fishnet,cntField,"DOUBLE")
            arcpy.CalculateField_management(fishnet,cntField,
                                            "!AREAKMMASKED!*!"+dsmField.name+"!","PYTHON")
        arcpy.Statistics_analysis(fishnet,sumTable,sumFields,"PIXELID")
        arcpy.AddIndex_management(sumTable,"PIXELID","PIXELID_index","UNIQUE")
        return 1
    except:
        return "There was and error processing " + fishnet + " " + str(arcpy.GetMessages())
    

def main():
    workspace = r'G:\gpw\global\fishnets'
    usaSpace = r'G:\gpw\usa\fishnets'
    tiledSpace = r'G:\gpw\tiled_countries\fishnets'
    workspaces = [r'\\Dataserver0\gpw\GPW4\Beta\Gridding\country\fishnets_and_clipped_water\rus\process']#usaSpace,tiledSpace
    # parse workspaces to make 1 master list
    gdb_list = []
    for ws in workspaces:
        arcpy.env.workspace = ws
        gdbs = arcpy.ListWorkspaces('rus_sa*',"FILEGDB")
        gdbs.sort(reverse=False)
        gdb_temp = [os.path.join(ws, gdb) for gdb in gdbs]
        for gdbt in gdb_temp:
            gdb_list.append(gdbt)    
       
    print "processing"
    print len(gdb_list)
##    for gdb in gdb_list:
##        print gdb
##        process(gdb)
    # create multi-process pool and execute tool
    pool = multiprocessing.Pool(processes=1,maxtasksperchild=1)
    results = pool.map(calcCounts, gdb_list)
    print(results)
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()
if __name__ == '__main__':
    main()















    
