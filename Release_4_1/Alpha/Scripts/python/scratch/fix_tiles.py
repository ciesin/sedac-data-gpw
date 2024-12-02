import arcpy, os, datetime, multiprocessing

def process(gdb):
    processTime = datetime.datetime.now()
    # grab clipMask
    arcpy.env.workspace = gdb
    clipMask = gdb + os.sep + str(arcpy.ListFeatureClasses("*boundaries_2010")[0])
    # grab intersect
    fishGDB = r'D:\gpw\stage\fishnets' + os.sep + os.path.basename(gdb)[:-4] + "_fishnet.gdb"
    arcpy.env.workspace = fishGDB
    fishnet = str(arcpy.ListFeatureClasses("*fishnet")[0])
    fishnetRn = fishnet + "_beta"
    if not arcpy.Exists(fishnetRn):
##        intersectIn = str(arcpy.ListFeatureClasses("*intersect")[0])
##        arcpy.Delete_management(intersectIn)
        arcpy.Rename_management(fishnet,fishnetRn)
##    intersectRn = intersectIn + "_v0"
##    if not arcpy.Exists(intersectRn):
##        arcpy.Rename_management(intersectIn,intersectRn)
##        fishDel = arcpy.ListFeatureClasses("*processed")[0]
##        arcpy.Delete_management(fishDel)
##        delTable = arcpy.ListTables("*table")[0]
##        arcpy.Delete_management(delTable)

        # clip it
##        arcpy.Clip_analysis(intersectRn,clipMask,intersectIn)
        # select by location
##        fishLyr = "fishlyr"
##        arcpy.MakeFeatureLayer_management(fishnetRn,fishLyr)
##        arcpy.SelectLayerByLocation_management(arcpy.MakeFeatureLayer_management(clipMask,"cllyr"),"INTERSECT",fishLyr)
##        arcpy.CopyFeatures_management(fishLyr,fishnet)
        arcpy.Clip_analysis(fishnetRn,clipMask,fishnet)
        return "processed " + gdb + " in " + str(datetime.datetime.now()-processTime)
    else:
        return "already processed " + gdb 

def main():
    scriptTime = datetime.datetime.now()
    # set workspaces and preprocess to attach paths
    inWS = r'D:\gpw\stage\pop_tables'
    #r'\\Dataserver0\gpw\GPW4\Release_4_0\Prod\Gridding\country\pop_tables'
    wildcards = ["grl*","bra*"]
    for wildcard in wildcards:
        arcpy.env.workspace = inWS
        workspaces = arcpy.ListWorkspaces(wildcard,"Folder")
        workspaces.sort()
        gdb_list = []
        for workspace in workspaces:        
            # describe the workspace
            workDesc = arcpy.Describe(workspace)
            # if it is "BRA, CAN, GRL, RUS, or USA" then it is nested in subfolder
            if str(workDesc.workspaceType)=="FileSystem":
                workspace = workspace + os.sep + "tiles"
                arcpy.env.workspace = workspace
                gdbs = arcpy.ListWorkspaces("*")
                for gdb in gdbs:
                    gdb_list.append(gdb)
##        i = 0
##        for gdb in gdb_list:
##            print gdb
##            i = i + 1
##        print i
##            print process(gdb)
        
    # multiprocess the data
    pool = multiprocessing.Pool(processes=23,maxtasksperchild=1)
    print pool.map(process, gdb_list) 
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()
    print "Script complete"
    print str(datetime.datetime.now()-scriptTime)

if __name__ == '__main__':
    main()
