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
    iso = os.path.basename(gdb)[:3]
    arcpy.env.workspace = gdb
    inFC = gdb + os.sep + str(arcpy.ListFeatureClasses("*gridding")[0])
    ######
    fishGDB = gdb.replace("pop_tables","fishnets").replace(".gdb","_fishnet.gdb")
    arcpy.env.workspace = fishGDB
    fishnet = fishGDB + os.sep + str(arcpy.ListFeatureClasses("*_fishnet")[0])
    ######
    # special for tiled countries
    waterGDB = os.path.dirname(os.path.dirname(gdb)) + os.sep + iso + ".gdb"
    waterFC = waterGDB + os.sep + iso + "_water_areas_mollweide"
    # intersect fishnet and inFC
    clipnetInt = 'in_memory' + os.sep + os.path.basename(fishnet) + "_intersect"
    projectFC = fishGDB + os.sep + os.path.basename(fishnet) + "_intersect_mollweide"
    # define spatial reference
    prjFile = r'D:\gpw\custom_projections' + os.path.sep + iso + "_fishnet_mollweide.prj"
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
            # write the values
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
    waterNet = "in_memory" + os.sep + rootName + "_water"
    # if the watermask is false then do final calculations 
    if arcpy.Exists(waterFC) == False:
        arcpy.CalculateField_management(clipnetInt,waterArea,0,'PYTHON')
    else:
        if not arcpy.Exists(waterNet):
            # clip projectFC to waterFC
            try:
                arcpy.Clip_analysis(projectFC, waterFC, waterNet)
            except:
                return "Watermask Clip Failed: " + str(arcpy.GetMessages())
            if not arcpy.Exists(waterNet):
                arcpy.CalculateField_management(clipnetInt,waterArea,0,'PYTHON')   
            else:
                # check if there are any features in waterNet
                count = arcpy.GetCount_management(waterNet)
                # if not then for final calculations
                if int(str(count))==0:
                    arcpy.CalculateField_management(clipnetInt,waterArea,0,'PYTHON')
                    arcpy.Delete_management(waterNet)
                else:
                    # otherwise
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
                        # write the values
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
    # finally write the outputs
    try:
        arcpy.CopyFeatures_management(clipnetInt,clipnetInt.replace("in_memory",fishGDB))
    except:
        return "Error in " + rootName + ": Writing Intersect Table to Disk"
    try:
        if arcpy.Exists(waterNet):
            if int(arcpy.GetCount_management(waterNet)[0])>0:
                arcpy.CopyFeatures_management(waterNet,waterNet.replace("in_memory",fishGDB))
            else:
                pass
        else:
            pass
    except:
        return "Error in " + rootName + ": Writing WaterNet to Disk"
    # success
    return "Intersected " + gdbName + ": " + str(datetime.datetime.now()-startTime)

    
def main():
    scriptTime = datetime.datetime.now()
    # set workspaces and preprocess to attach paths
    inWS = r'D:\gpw\stage\pop_tables'
    arcpy.env.workspace = inWS
    workspaces = arcpy.ListWorkspaces("*","FOLDER")
    workspaces = [workspace+os.sep+'tiles' for workspace in workspaces]
    workspaces.sort()
    gdb_list = []
    for ws in workspaces:
        if ws ==r'D:\gpw\stage\pop_tables\rus\tiles':
            continue
    
        arcpy.env.workspace = ws
        gdbs = arcpy.ListWorkspaces("*")
        for gdb in gdbs:
            gdb_list.append(gdb)
    print len(gdb_list)
##    for gdb in gdb_list:
##        print gdb
##        print intersect(gdb)
##        break
    # multiprocess the data
    try:
        pool = multiprocessing.Pool(processes=26,maxtasksperchild=1)
        print pool.map(intersect, gdb_list)
        # Synchronize the main process with the job processes to
        # ensure proper cleanup.
        pool.close()
        pool.join()
    except:
        print sys.stdout
        pool.close()
        pool.join()
    print "Script complete"
    print str(datetime.datetime.now()-scriptTime)
if __name__ == '__main__':
    main()















    
