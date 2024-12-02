# this script reads "ADMINAREAKMMASKED" into memory and
# calculates administrative level densities and writes them
# to the estimates table

import arcpy, os, datetime, multiprocessing, socket
def grid(fishnet, gridFields, gdb):
    arcpy.env.overwriteOutput = True
    startTime = datetime.datetime.now()
    inWS = os.path.dirname(gdb)
    outWS = inWS.replace(os.path.basename(inWS),'country_tifs')
    iso = os.path.basename(gdb)[:3]
    rootName = os.path.basename(gdb)[:-4]
    if iso == rootName:
        outFolders = [outWS + os.sep + rootName]
    else:
        outFolders = [outWS + os.sep + iso]
        outFolders.append(outFolders[0]+os.sep+rootName)
    for outFolder in outFolders:
        try:
            if not arcpy.Exists(outFolder):
                os.mkdir(outFolder)
        except:
            return (0,"Cannot create Folder: " + outFolder)
    outFolder = outFolders[-1]                      
    # create raster
    # Coordinate System
    wgs84 = arcpy.SpatialReference(4326)
    # Describe Fish
    desc = arcpy.Describe(fishnet)
    # Calculate Raster Extent
    extent = desc.Extent
    xmin = int(round(extent.XMin - .5))
    xmax = int(round(extent.XMax + .5))
    ymin = int(round(extent.YMin - .5))
    ymax = int(round(extent.YMax + .5))
    # Lines per degree, determines the output resolution 120 = 30 arc-seconds resolution
    # 1 degree divided into 120 parts is 30 seconds
    linespd = 120 ## Update As Needed
    cellSize = 1.0 / linespd
    for gridField in gridFields:
        outGrid = outFolder + os.sep + rootName.upper() + "_" + gridField + ".tif"           
        try:
            arcpy.PolygonToRaster_conversion(fishnet,gridField,outGrid,'CELL_CENTER','#',cellSize)
        except:
            return (0,"Error creating Grid for: " + rootName + " : " + gridField + " : " + str(arcpy.GetMessages()))
    return (1,"Created grids for " + rootName + ": " + str(datetime.datetime.now()-startTime))        
        
def calculateGridCounts(gdb):
    startTime = datetime.datetime.now()
    iso = os.path.basename(gdb)[:3]
    rootName = os.path.basename(gdb)[:-4]
    try:
        arcpy.env.workspace = gdb
        # grab intersectTable
        intersectTable = arcpy.ListTables("*_table")[0]
        fishnet = arcpy.ListFeatureClasses("*_fishnet")[0]
        finalFishnet = fishnet + "_processed"
        if arcpy.Exists(finalFishnet):
            arcpy.Delete_management(finalFishnet)
##            gridResult = grid(finalFishnet, updateFields, gdb)
##            if gridResult[0]==0:
##                return gridResult
##            else:
##                return rootName + " : already processed counts, calculated grids"
        # create list of fields to generate statistics for
        statsFields = [["BOUNDARY_CONTEXT","MAX"],["MASKEDAREA","MEAN"],["WATERAREAKM","SUM"],["AREAKMMASKED","SUM"]]
        # list CNTM fields in order to be flexible to whatever variables
        # are present in the country
        cntFields = arcpy.ListFields(intersectTable,"*CNTM")
        [statsFields.append([field.name,"SUM"]) for field in cntFields]
        # create a summary table in memory
        memSumTbl = 'in_memory' + os.sep + os.path.basename(intersectTable) + "_summary"
        try:
            arcpy.Statistics_analysis(intersectTable,memSumTbl,statsFields,"PIXELID")
        except:
            return "Error in " + rootName + " : making table views " + str(arcpy.GetMessages())
        # read the fishnet into memory
        memFishnet = 'in_memory' + os.sep + os.path.basename(fishnet) + "_view"
        try:
            arcpy.CopyFeatures_management(fishnet,memFishnet)
        except:
            return "Error in " + rootName + " : making fishnet in memory"
        # define initial list of searchFields
        searchFields = ["PIXELID"]
        updateFields = ["PIXELID"]
        # create list of variables
        variables = arcpy.ListFields(memSumTbl,"*")
        for variable in variables:
            name = variable.name
            if name == "OBJECTID":
                continue
            elif name == "PIXELID":
                continue
            elif name == "FREQUENCY":
                newField = "NUMINPUTS"
            elif name == "MAX_BOUNDARY_CONTEXT":
                newField = "BOUNDARY_CONTEXT"
            elif name == "MEAN_MASKEDAREA":
                newField = "MEAN_MASKEDADMINAREA"
            else:
                newField =  name.replace("SUM_","")
            # add the field
            arcpy.AddField_management(memFishnet,newField,"FLOAT")
            # append the newField to updateFields, and the variable.name to searchFields
            updateFields.append(newField)
            searchFields.append(name)
        # create dictionary to hold source counts
        counts = {}
        try:
            # read the values
            with arcpy.da.SearchCursor(memSumTbl,searchFields) as rows:
                for row in rows:
                    # store with PIXELID as key and a tuple of estimates as value
                    pixelid = row[0]
                    value = row
                    counts[pixelid] = value
        except:
            return "Error in " + rootName + ": Creating Counts Dictionary"
        # write the estimates to the memFishnet
        try:
            # read the values
            with arcpy.da.UpdateCursor(memFishnet,updateFields) as rows:
                for row in rows:
                    # grab the pixelid
                    pixelid = row[0]
                    if pixelid not in counts:
                        continue
                    # set the fields
                    i = 0
                    for field in updateFields:                        
                        if i < 1:
                            i = i + 1                            
                            pass
                        else:
                            # calculate the counts
                            row[i]= counts[pixelid][i]
                            i = i + 1
                    
                    # update the row
                    rows.updateRow(row)
                    
        except:
            return "Error in " + rootName + ": Writing Updates"
        # finally write the final fishnet
        try:
            arcpy.CopyFeatures_management(memFishnet,finalFishnet)
        except:
            return "Error in " + rootName + ": Writing Table to Disk"
        # grid the result
        try:
            gridResult = grid(finalFishnet, updateFields, gdb)
            if gridResult[0]==0:
                return gridResult
            
        except:
            return "Error in " + rootName + ": Gridding"
            
        # success
        return "Calculated counts and Rasters for " + rootName + ": " + str(datetime.datetime.now()-startTime)
    except:
        return rootName + " error: " + str(arcpy.GetMessages())
    

def main():
    scriptTime = datetime.datetime.now()
    # set workspaces and preprocess to attach paths
    host = socket.gethostname()
    if host == 'Devsedarc3':
        inWS = r'F:\gpw\release_4_1\process'
    elif host == 'Devsedarc4':
        inWS = r'D:\gpw\release_4_1\process'
    #r'\\Dataserver0\gpw\GPW4\Release_4_0\Prod\Gridding\country\pop_tables'
    arcpy.env.workspace = inWS
    workspaces = [os.path.join(inWS,workspace) for workspace in arcpy.ListWorkspaces("*","FILEGDB")]
    workspaces.sort()
    # multiprocess the data
    pool = multiprocessing.Pool(processes=20,maxtasksperchild=1)
    results = pool.map(calculateGridCounts, workspaces)
    for result in results:
        print result
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()
    print "Script complete"
    print str(datetime.datetime.now()-scriptTime)

if __name__ == '__main__':
    main()
