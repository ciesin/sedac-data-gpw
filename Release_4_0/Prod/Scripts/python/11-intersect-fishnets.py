# use multiprocessing to intersect fishnets
# with administrative boundaries that have calculated
# their ADMINAREAKMMASKED, and have a UBID

import arcpy, os, multiprocessing, datetime

def intersect(gdb):
    startTime = datetime.datetime.now()
    arcpy.env.scratchWorkspace = "in_memory"
    # define inputs
    gdbName = os.path.basename(gdb)
    rootName = os.path.basename(gdb)[:-4]
    arcpy.env.workspace = gdb
    inFC = gdb + os.sep + str(arcpy.ListFeatureClasses("*gridding")[0])
    fishGDB = gdb.replace("pop_tables","fishnets").replace(".gdb","_fishnet.gdb")
    arcpy.env.workspace = fishGDB
    fishnet = fishGDB + os.sep + str(arcpy.ListFeatureClasses("*_fishnet")[0])
    # intersect fishnet and inFC
    clipnetInt = fishnet + "_intersect"
    projectFC = clipnetInt + "_mollweide"
    # define spatial reference
    prjFile = r'D:\gpw\custom_projections' + os.path.sep + rootName + "_fishnet_mollweide.prj"
    # check to see that estimates exists, if it doesn't kill the script
    if not arcpy.Exists(prjFile):
        print "The input prj file does not exist, check the network"
    else:
        spatialRef = open(prjFile,"r").read()
    inFeatures = [inFC,fishnet]
    if not arcpy.Exists(projectFC):
        try:
            arcpy.Intersect_analysis(inFeatures, clipnetInt)
            arcpy.AddField_management(clipnetInt,"INTERSECTID","LONG")
            arcpy.CalculateField_management(clipnetInt,"INTERSECTID",
                                            "!OBJECTID!","PYTHON")
            arcpy.AddField_management(clipnetInt,"AREAKM",'DOUBLE')
            arcpy.AddField_management(clipnetInt,"WATERAREAKM",'DOUBLE')
            arcpy.AddField_management(clipnetInt,"AREAKMMASKED",'DOUBLE')
            arcpy.Project_management(clipnetInt, projectFC, spatialRef)
            arcpy.CalculateField_management(projectFC,"AREAKM",
                                            '!shape.area@SQUAREKILOMETERS!'
                                            ,'PYTHON')
        except:
            return "Error in: " + gdbName + " : " + str(arcpy.GetMessages())

        # join ADMINAREAKM to inFCG
        adminArea = "AREAKM"
        # create dictionary to hold values
        values = {}
        try:
            # read the values
            with arcpy.da.SearchCursor(projectFC,["INTERSECTID",adminArea]) as rows:
                for row in rows:
                    # store with AGEID as key and a tuple of numbers as value
                    key = row[0]
                    value = row[1]
                    values[key] = value
        except:
            return "Error in " + gdbName + ": Creating Value Dictionary"
        try:
            # read the values
            with arcpy.da.UpdateCursor(clipnetInt,["INTERSECTID",adminArea]) as rows:
                for row in rows:
                    # grab the ubid
                    ubid = row[0]
                    row[1] = values[ubid]
                    # update the row
                    rows.updateRow(row)
        except:
            return "Error in " + gdbName + ": Writing Value Dictionary"
    # define input waterMask
    waterArea = "WATERAREAKM"
    waterFC = gdb + os.sep + rootName + "_water_areas_mollweide"
    waterNet = "in_memory" + os.sep + rootName + "_water"
    # if the watermask is false then do final calculations and return
    if arcpy.Exists(waterFC) == False:
        arcpy.CalculateField_management(clipnetInt,waterArea,0,'PYTHON')
    else:
        if not arcpy.Exists(waterNet):
            # clip projectFC to waterFC
            try:
                arcpy.Clip_analysis(projectFC, waterFC,waterNet)
            except:
                return "Watermask Clip Failed: " + str(arcpy.GetMessages())
            # check if there are any features
            if int(arcpy.GetCount_management(waterNet)[0])<1:
                arcpy.CalculateField_management(clipnetInt,waterArea,0,'PYTHON')
            else:
                # calculate water areas
                arcpy.CalculateField_management(waterNet,waterArea,'!shape.area@SQUAREKILOMETERS!','PYTHON')
                # join ADMINAREAKM to inFCG
                # create dictionary to hold values
                values = {}
                try:
                    # read the values
                    with arcpy.da.SearchCursor(waterNet,["INTERSECTID",waterArea]) as rows:
                        for row in rows:
                            # store with AGEID as key and a tuple of numbers as value
                            key = row[0]
                            value = row[1]
                            values[key] = value
                except:
                    return "Error in " + gdbName + ": Creating Water Value Dictionary"
                
                try:
                    # read the values
                    with arcpy.da.UpdateCursor(clipnetInt,["INTERSECTID",waterArea]) as rows:
                        for row in rows:
                            # grab the ubid
                            ubid = row[0]
                            if ubid in values:
                                row[1] = values[ubid]
                            else:
                                row[1] = 0
                            # update the row
                            rows.updateRow(row)
                except:
                    return "Error in " + gdbName + ": Writing Water Value Dictionary"
    # calculate masked area
    maskedArea = "AREAKMMASKED"
    adminArea = "AREAKM"
    # Need to convert Negatives to Zeros
    arcpy.CalculateField_management(clipnetInt,maskedArea,'!' + adminArea + '! - !' + waterArea + "!",'PYTHON')
    try:
        maskedLYR = rootName + "_maskedlyr"
        arcpy.MakeFeatureLayer_management(clipnetInt,maskedLYR,maskedArea + " < 0.0000001")
        count = arcpy.GetCount_management(maskedLYR)[0]
        if not int(str(count))==0:
            arcpy.CalculateField_management(maskedLYR,maskedArea,0, "PYTHON")    
    except:
        return "Error calc: masked negatives: " + str(arcpy.GetMessages())
    # success
    return "Intersected " + gdbName + ": " + str(datetime.datetime.now()-startTime)

    
def main():
    scriptTime = datetime.datetime.now()
    # set workspaces and preprocess to attach paths
    inWS = r'D:\gpw\stage\pop_tables'
    #r'\\Dataserver0\gpw\GPW4\Release_4_0\Prod\Gridding\country\pop_tables'
    arcpy.env.workspace = inWS
    workspaces = arcpy.ListWorkspaces("*","FILEGDB")
    workspaces.sort()
    gdb_list = []
    for workspace in workspaces:
##        # describe the workspace
##        workDesc = arcpy.Describe(workspace)
##        # if it is "BRA, CAN, GRL, RUS, or USA" then it is nested in subfolder
##        if str(workDesc.workspaceType)=="FileSystem":
##            workspace = workspace + os.sep + os.path.basename(workspace)+".gdb"
        gdb_list.append(workspace) 
##    for gdb in gdb_list:
##        print gdb
##        print intersect(gdb)
    # multiprocess the data
##    print gdb_list
    pool = multiprocessing.Pool(processes=22,maxtasksperchild=1)
    print pool.map(intersect, gdb_list) 
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()
    print "Script complete"
    print str(datetime.datetime.now()-scriptTime)
if __name__ == '__main__':
    main()















    
