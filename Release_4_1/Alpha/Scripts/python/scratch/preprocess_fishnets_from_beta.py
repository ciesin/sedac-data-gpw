# this script reads "ADMINAREAKMMASKED" into memory and
# calculates administrative level densities and writes them
# to the estimates table

import arcpy, os, datetime, multiprocessing

def preprocessBetaIntersectedFishnets(gdb):
    startTime = datetime.datetime.now()
    iso = os.path.basename(gdb)[:3]
    gdbName = os.path.basename(gdb)[:-4]
    outWS = r'D:\gpw\stage\fishnets'
    outGDB = outWS + os.sep + gdbName + ".gdb"
    if arcpy.Exists(outGDB):
        return gdbName + " already exists"
    # create new gdb    
    arcpy.CreateFileGDB_management(outWS,gdbName)
    arcpy.env.workspace = gdb
    try:
##        intersectedFishnet = arcpy.ListFeatureClasses("*_intersect")[0]
        fishnet = arcpy.ListFeatureClasses("*_fishnet")[0]
        # list all fields
##        fields = arcpy.ListFields(intersectedFishnet,"*")
        fishFields = arcpy.ListFields(fishnet,"*")
        # declare the fields to keep
        keepFields = ["OBJECTID","SHAPE","UBID", "PIXELID","SHAPE_Length","SHAPE_Area"]
##        fldInfo = arcpy.FieldInfo()
##        [fldInfo.addField(field.name,field.name,"VISIBLE","NONE") if field.name in keepFields else fldInfo.addField(field.name,field.name,"HIDDEN","NONE") for field in fields]
        fishfldInfo = arcpy.FieldInfo()
        [fishfldInfo.addField(field.name,field.name,"VISIBLE","NONE") if field.name in keepFields else fishfldInfo.addField(field.name,field.name,"HIDDEN","NONE") for field in fishFields]

##        # determine fields to delete
##        delFields = [field.name for field in fields if field.name not in keepFields]
##        # delete them
##        try:
##            if len(delFields)>0:
##    
##                arcpy.DeleteField_management(intersectedFishnet,delFields)
##        except:
##            return "Error in " + iso + ": Deleting Fields" + " :  " + arcpy.GetMessages()
        # rather than delete fields, instead make a feature layer with only the keep fields and
        fl = gdbName + "_layer"
        fishFl = gdbName + "_layer2"
        try:
##            arcpy.MakeFeatureLayer_management(intersectedFishnet,fl,"#","#",fldInfo)
            arcpy.MakeFeatureLayer_management(fishnet,fishFl,"#","#",fishfldInfo)
        except:
            return "Unable to create feature layer for: " + iso
##        # copy features
##        outFC = outGDB + os.sep + os.path.basename(intersectedFishnet)
##        try:
##            arcpy.CopyFeatures_management(fl,outFC)
##        except:
##            return "Unable to copy features for: " + iso
        # finally copy fishnet
        outFish = outGDB + os.sep + os.path.basename(fishnet)
        try:
            arcpy.CopyFeatures_management(fishFl,outFish)
        except:
            return "Unable to copy fishnet for: " + iso
        # success
        return "Preprocessed " + iso + ": " + str(datetime.datetime.now()-startTime)
    except:
        return iso + " error: " + str(arcpy.GetMessages())
    

def main():
    scriptTime = datetime.datetime.now()
    # set workspaces and preprocess to attach paths
    inWS = r'D:\gpw\beta_fishnets'
    #r'\\Dataserver0\gpw\GPW4\Release_4_0\Prod\Gridding\country\pop_tables'
    wildcards = ["a*","bdi*","bel*","ben*","bes*","bfa*","bgd*","bgr*"]
    gdb_list = []
    for wildcard in wildcards:
        arcpy.env.workspace = inWS
        workspaces = arcpy.ListWorkspaces(wildcard,"FileGDB")
        workspaces.sort()
        for workspace in workspaces:
            arcpy.env.workspace = workspace
            # describe the workspace
            workDesc = arcpy.Describe(workspace)
            # if it is "BRA, CAN, GRL, RUS, or USA" then it is nested in subfolder
            if str(workDesc.workspaceType)=="FileSystem":
##                print workspace
                arcpy.env.workspace = workspace
                gdbs = arcpy.ListWorkspaces("*")
                gdb_list = gdb_list + gdbs
            else:
                gdb_list.append(workspace) 
##    i = 0
##    print len(gdb_list)
##    for gdb in gdb_list:
##        print gdb
##        i = i + 1
##    print i
##        print preprocessBetaIntersectedFishnets(gdb)
    # multiprocess the data
    pool = multiprocessing.Pool(processes=22,maxtasksperchild=1)
    print pool.map(preprocessBetaIntersectedFishnets, gdb_list) 
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()
    print "Script complete"
    print str(datetime.datetime.now()-scriptTime)

if __name__ == '__main__':
    main()
