# use multiprocessing to intersect fishnets
# with administrative boundaries that have calculated
# their ADMINAREAKMMASKED, and have a UBID

import arcpy, os, multiprocessing, datetime, socket
arcpy.env.overwriteOutput = True
def intersect(inFeatures,intersectOut):
        try:
            if not arcpy.Exists(intersectOut):
                arcpy.Intersect_analysis(inFeatures, intersectOut)
                arcpy.AddField_management(intersectOut,"INTERSECTID","LONG")
                arcpy.CalculateField_management(intersectOut,"INTERSECTID",
                                                "!OBJECTID!","PYTHON")
                arcpy.AddField_management(intersectOut,"AREAKM",'DOUBLE')
                arcpy.AddField_management(intersectOut,"WATERAREAKM",'DOUBLE')
                arcpy.AddField_management(intersectOut,"AREAKMMASKED",'DOUBLE')
            return (1, intersectOut)
        except:
            return (0,"Error intersect: " + str(inFeatures))

def tableToDict(table,searchFields):
    values = {}
    # read the values
    with arcpy.da.SearchCursor(table,searchFields) as rows:
        for row in rows:
            # store with UBID as key and a tuple of numbers as value
            key = row[0]
            value = row[1]
            values[key] = value
    return values

def dictToTable(table,updateFields,values):
    with arcpy.da.UpdateCursor(table,updateFields) as rows:
        for row in rows:
            # grab the id
            uid = row[0]
            row[1] = values[uid]
            # update the row
            rows.updateRow(row)
    return table

def addPixelArea(iso,inFish,fishProj,outFish,spatialRef):
    arcpy.Project_management(inFish,fishProj,spatialRef)
    arcpy.AddField_management(fishProj,"PIXELID","LONG")
    arcpy.AddField_management(fishProj,"PIXELAREA","DOUBLE")
    arcpy.CalculateField_management(fishProj,"PIXELAREA",
                                            '!shape.area@SQUAREKILOMETERS!'
                                            ,'PYTHON')
    # read into dictionary
    try:
        values = tableToDict(fishProj,['gridcode','PIXELAREA'])
    except:
        return (0,"Error in " + inFish + ": Creating Value Dictionary")
    # copy the fishnet into memory
    inMemFish = 'in_memory' + os.sep + iso + "_fish"
    arcpy.CopyFeatures_management(inFish,inMemFish)
    arcpy.AddField_management(inMemFish,"PIXELID","LONG")
    arcpy.AddField_management(inMemFish,"PIXELAREA","DOUBLE")
    try:
        with arcpy.da.UpdateCursor(inMemFish,["gridcode","PIXELID","PIXELAREA"]) as rows:
            for row in rows:
                # grab the id
                uid = row[0]
                row[1] = uid
                row[2] = values[uid]
                # update the row
                rows.updateRow(row)
    except:
        return (0,"Error in " + inMemFish + ": Writing Updates")
    # copy the table to disk
    arcpy.CopyFeatures_management(inMemFish,outFish)
    return(1, outFish)
def process(gdb):
    startTime = datetime.datetime.now()
    try:
        # define inputs
        gdbName = os.path.basename(gdb)
        iso = os.path.basename(gdb)[:-4]
        arcpy.env.workspace = gdb
        inFC = gdb + os.sep + str(arcpy.ListFeatureClasses("*gridding")[0])
        # define spatial reference
        host = socket.gethostname()
        if host == 'Devsedarc3':
            prjFile = r'F:\gpw\custom_projections' + os.path.sep + iso + "_fishnet_mollweide.prj"
        elif host == 'Devsedarc4':
            prjFile = r'D:\gpw\custom_projections' + os.path.sep + iso + "_fishnet_mollweide.prj"
        # check to see that prj exists, if it doesn't kill the script
        if not arcpy.Exists(prjFile):
            return (0,"The input prj file for " + iso + " does not exist, check the network",prjFile)
        else:
            spatialRef = open(prjFile,"r").read()
        # calculate pixelid on inFish
        fishGDB = r'\\dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\fishnets\output_fishnets' + os.sep + iso + '.gdb'
        arcpy.env.workspace = fishGDB
        inFish = fishGDB + os.sep + str(arcpy.ListFeatureClasses("*_fishnet")[0])
        outFish = gdb + os.sep + iso + "_fishnet"        
    except:
        return iso + " error getting prj and fishnet"
    try:
        # intersect inFC and bcFC with fishnet
        fishnet = outFish
        fc= inFC.replace("_gridding","_boundary_context")
        if arcpy.Exists(fc):
            intersectIn = fc + "_intersect"
            if arcpy.Exists(fc):
                intersectFile = intersectIn
                projectFC = intersectFile + "_mollweide"
                searchFields = ["INTERSECTID","AREAKM"]
                # read into dictionary
                try:
                    values = tableToDict(projectFC,searchFields)
                except:
                    return "Error in " + projectFC + ": Creating Value Dictionary"
                # copy into memory
                inMem = 'in_memory' + os.sep + os.path.basename(fc)
                arcpy.CopyFeatures_management(intersectIn,inMem)
                try:
                    inMem = dictToTable(inMem,searchFields,values)
                except:
                    return "Error in " + inMem + ": Writing Updates"
                # copy the table to disk
                arcpy.CopyFeatures_management(inMem,intersectIn)
                # copy waterarea if waterFC exists
                waterMask = r'D:\gpw\release_4_1\water\water_outputs\water_masks' + os.sep + iso + "_water_mask.shp"
                if arcpy.Exists(waterMask):
                        try:
                                waterFC = gdb+os.sep+iso+"_boundary_context_water_features"
                                arcpy.Clip_analysis(fc,waterMask,waterFC)
                                projectFC = waterFC + "_mollweide"
                                arcpy.Project_management(waterFC, projectFC, spatialRef)
                                waterClip = waterFC + "_intersect_mollweide"
                                arcpy.Clip_analysis(fc + "_intersect_mollweide",projectFC,waterClip)
                                arcpy.CalculateField_management(waterClip,"WATERAREAKM",
                                            '!shape.area@SQUAREKILOMETERS!'
                                            ,'PYTHON')
                        except:
                                return iso + " error with water clipping, check geometry"

                        searchFields = ["INTERSECTID","WATERAREAKM"]
                        # read into dictionary
                        try:
                                values = tableToDict(waterClip,searchFields)
                        except:
                                return "Error in " + waterClip + ": Creating Value Dictionary"

                        # copy into memory
                        inMem = 'in_memory' +  os.sep + os.path.basename(fc) + "_2"
                        arcpy.CopyFeatures_management(fc + "_intersect",inMem)
                        updateFields = ["INTERSECTID","WATERAREAKM","AREAKM","AREAKMMASKED"]
        ##                return str(arcpy.da.UpdateCursor(inMem,updateFields))
                        with arcpy.da.UpdateCursor(inMem,updateFields) as rows:
                                for row in rows:
                                        try:
                                                # grab the id
                                                uid = row[0]
                                                if uid in values.keys():
                                                        row[1] = values[uid]
                                                else:
                                                        row[1] = 0
                                                maskedArea = row[2] - row[1]        
                                                if maskedArea < 0.0000001 :
                                                        maskedArea = 0
                                                row[3] = maskedArea
                                        
                                                # update the row
                                                rows.updateRow(row)
                                                
                                        except:
                                                return row
                                        
                        # copy the table to disk
                        arcpy.CopyFeatures_management(inMem,fc + "_intersect")
                else:
                    arcpy.CalculateField_management(fc + "_intersect","WATERAREAKM",0,"PYTHON")
                    arcpy.CalculateField_management(fc + "_intersect","AREAKMMASKED","!AREAKM!","PYTHON")
                # success
                return "Intersected " + gdbName + ": " + str(datetime.datetime.now()-startTime)
      
    except:
        return iso + " error in intersections"
def main():
    scriptTime = datetime.datetime.now()
    host = socket.gethostname()
    if host == 'Devsedarc3':
        workspace = r'F:\gpw\release_4_1\process'
    elif host == 'Devsedarc4':
        workspace = r'D:\gpw\release_4_1\process'
    arcpy.env.workspace = workspace
    print "processing"
    # must create procList
    gdbs= arcpy.ListWorkspaces("*","FILEGDB")
    print str(len(gdbs)) + " countries"
    procList = [os.path.join(workspace,gdb) for gdb in gdbs]
    pool = multiprocessing.Pool(processes=20,maxtasksperchild=1)
    results = pool.map(process, procList)
    for result in results:
        print result
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()
    print "Script Complete in " + str(datetime.datetime.now()-scriptTime)
if __name__ == '__main__':
    main()
        
