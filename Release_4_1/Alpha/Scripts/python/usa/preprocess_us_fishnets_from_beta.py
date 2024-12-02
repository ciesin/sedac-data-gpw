# this script reads "ADMINAREAKMMASKED" into memory and
# calculates administrative level densities and writes them
# to the estimates table

import arcpy, os, datetime, multiprocessing

def preprocessBetaIntersectedFishnets(gdb):
    startTime = datetime.datetime.now()
    iso = os.path.basename(gdb)[:6]
    gdbName = os.path.basename(gdb)[:-4]
    outWS = r'H:\gpw\fishnets'
    outGDB = outWS + os.sep + gdbName + ".gdb"
    if arcpy.Exists(outGDB):
        return gdbName + " already exists"
    # create new gdb    
    arcpy.CreateFileGDB_management(outWS,gdbName)
    # grab files to copy
    arcpy.env.workspace = gdb
    try:
        intersectedFishnet = arcpy.ListFeatureClasses("*_intersect")[0]
        fishnet = arcpy.ListFeatureClasses("*_fishnet")[0]
        # list all fields
        fields = arcpy.ListFields(intersectedFishnet,"*")
        # declare the fields to keep
        keepFields = ["OBJECTID","Shape","UBID","ADMINAREAKM","ADMINWATERAREAKM","ADMINAREAKMMASKED",
                      "PIXELID","Shape_Length","Shape_Area","AREAKM","WATERAREAKM","AREAKMMASKED"]
        fldInfo = arcpy.FieldInfo()
        [fldInfo.addField(field.name,field.name,"VISIBLE","NONE") if field.name in keepFields else fldInfo.addField(field.name,field.name,"HIDDEN","NONE") for field in fields]
##        # determine fields to delete
##        delFields = [field.name for field in fields if field.name not in keepFields]
##        # delete them
##        try:
##            if len(delFields)>0:
##                arcpy.DeleteField_management(intersectedFishnet,delFields)
##        except:
##            return "Error in " + iso + ": Deleting Fields"
        # rather than delete fields, instead make a feature layer with only the keep fields and
        fl = gdbName + "_layer"
        try:
            arcpy.MakeFeatureLayer_management(intersectedFishnet,fl,"#","#",fldInfo)
        except:
            return "Unable to create feature layer for: " + iso
        # copy features
        outFC = outGDB + os.sep + os.path.basename(intersectedFishnet)
        try:
            arcpy.CopyFeatures_management(fl,outFC)
        except:
            return "Unable to copy features for: " + iso
        # finally copy fishnet
        outFish = outGDB + os.sep + os.path.basename(fishnet)
        try:
            arcpy.CopyFeatures_management(fishnet,outFish)
        except:
            return "Unable to copy fishnet for: " + iso
        
        # success
        return "Preprocessed " + iso + ": " + str(datetime.datetime.now()-startTime)
    except:
        return iso + " error: " + str(arcpy.GetMessages())
    

def main():
    scriptTime = datetime.datetime.now()
    # set workspaces and preprocess to attach paths
    inWS = r'H:\gpwBeta\usa\fishnets'
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
##    for gdb in gdb_list:
##        print gdb
##        print preprocessBetaIntersectedFishnets(gdb)
    # multiprocess the data
    pool = multiprocessing.Pool(processes=5,maxtasksperchild=1)
    print pool.map(preprocessBetaIntersectedFishnets, gdb_list) 
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()
    print "Script complete"
    print str(datetime.datetime.now()-scriptTime)

if __name__ == '__main__':
    main()
