# multiprocess template
import os, datetime, socket
import multiprocessing
import arcpy
scriptTime = datetime.datetime.now()
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
            if uid in values:
                row[1] = values[uid]
            else:
                row[1] = 0
            # update the row
            rows.updateRow(row)
    return table
def transferAttributes(outGDB,spatialRef,attributeTransferFile,intersectMem):
    if attributeTransferFile.split("_")[-1]=='water':
        searchFields=["INTERSECTID","WATERAREAKM"]
        calcField="WATERAREAKM"
    else:
        searchFields=["INTERSECTID","AREAKM"]
        calcField="AREAKM"
    intersectOut = attributeTransferFile.replace('in_memory',outGDB)
    intersectMoll = intersectOut + "_mollweide"
    # project
    try:
        arcpy.Project_management(attributeTransferFile, intersectMoll, spatialRef)
    except:
        return ('Error','Projecting ' + attributeTransferFile + " " + arcpy.GetMessages())
    # calculate area
    try:
        arcpy.CalculateField_management(intersectMoll,calcField,
                                            '!shape.area@SQUAREKILOMETERS!'
                                            ,'PYTHON')
    except:
        return ('Error','Calculating ' + calcField + " for " + attributeTransferFile)
    # read calculation into dictionary
    try:
        values = tableToDict(intersectMoll,searchFields)
    except:
        return ('Error',': Creating Value Dictionary for ' + intersectMoll)
    # write the values to attributeTransferFile
    try:
        values = dictToTable(intersectMem,searchFields,values)
    except:
        return ('Error',': Writing Values from Dictionary for ' + attributeTransferFile)
    # if the process succeeds
    return ("Success")
    
def process(outGDB):
    processTime = datetime.datetime.now()
    iso = os.path.basename(outGDB)[:-4]
    try:
        host = socket.gethostname()
        if host == 'Devsedarc3':
            inFCGDB = r'F:\gpw\release_4_1\input_data\country_boundaries_hi_res.gdb'
            prjFile = r'F:\gpw\custom_projections' + os.path.sep + iso + "_fishnet_mollweide.prj"
            waterMask = r'F:\gpw\release_4_1\water\water_outputs\water_masks' + os.sep + iso + "_water_mask.shp"
            templateBoundaries = r'F:\gpw\release_4_1\loading\templates.gdb\gridding_boundaries'
        elif host == 'Devsedarc4':
            inFCGDB = r'D:\gpw\release_4_1\input_data\country_boundaries_hi_res.gdb'
            prjFile = r'D:\gpw\custom_projections' + os.path.sep + iso + "_fishnet_mollweide.prj"
            waterMask = r'D:\gpw\release_4_1\water\water_outputs\water_masks' + os.sep + iso + "_water_mask.shp"
            templateBoundaries = r'D:\gpw\release_4_1\loading\templates.gdb\gridding_boundaries'
        # check for inFC
        arcpy.env.workspace = inFCGDB
        inFC = arcpy.ListFeatureClasses(iso+"*")
        if len(inFC)==0:
            return iso + " is missing inFC"
        elif len(inFC)>1:
            for f in inFC:
                if f[0:f.find('admin')-1] == iso:
                    inFC = os.path.join(inFCGDB,f)
        else:
            inFC = os.path.join(inFCGDB,inFC[0])
        # check if the country has a water mask
        if not arcpy.Exists(waterMask):
            hasWater = 0
        else:
            hasWater = 1
        # check for the countries custom PRJ file
        # define spatial reference
        # if it doesn't kill the script
        if not arcpy.Exists(prjFile):
            prjFile = r'D:\gpw\custom_projections' + os.path.sep + iso[:3] + "_fishnet_mollweide.prj"
            if not arcpy.Exists(prjFile):
                return prjFile + ": The input prj file does not exist, check the network"
            else:
                spatialRef = open(prjFile,"r").read()
        else:
            spatialRef = open(prjFile,"r").read()
        # load the boundaries into memory
        # copy of inFC
        inFCG = 'in_memory' + os.sep + os.path.basename(inFC) + "_gridding"
        try:
            arcpy.CreateFeatureclass_management("in_memory",os.path.basename(inFC) + "_gridding","POLYGON",
                                                templateBoundaries,"DISABLED","DISABLED",
                                                arcpy.SpatialReference(4326))
            # append inFCG to outFile
            arcpy.Append_management(inFC,inFCG,"NO_TEST")
            # calculate the ISO field
            arcpy.CalculateField_management(inFCG,"ISO",'"' + iso[:3].upper() + '"',"PYTHON")
            arcpy.AddField_management(inFCG,"AREAKM",'DOUBLE')
            arcpy.AddField_management(inFCG,"WATERAREAKM",'DOUBLE')
            arcpy.AddField_management(inFCG,"MASKEDAREAKM",'DOUBLE')
        except:
            return iso + " error creating " + inFCG + " " + arcpy.GetMessages()
        # grab the fishnet
        arcpy.env.workspace = outGDB
        fishnet = arcpy.ListFeatureClasses("*fishnet")[0]
        # intersect the boundaries with the fishnet
        intersectMem = 'in_memory' + os.sep + os.path.basename(inFC) + "_intersect"
        arcpy.Intersect_analysis([inFCG,fishnet], intersectMem)
        arcpy.AddField_management(intersectMem,"INTERSECTID","LONG")
        arcpy.CalculateField_management(intersectMem,"INTERSECTID",
                                        "!OBJECTID!","PYTHON")
        # if the country has water features create an intersected fishnet
        # version of them
        if hasWater == 1:
            intersectWaterMem = 'in_memory' + os.sep + os.path.basename(inFC) + "_intersect_water"
            arcpy.Clip_analysis(intersectMem,waterMask,intersectWaterMem)
            attributeTransferFiles = [intersectMem,intersectWaterMem]
        else:
            attributeTransferFiles = [intersectMem]
        # for each of the attribute transfer files run the subprocess
        for attributeTransferFile in attributeTransferFiles:
            intersectCalc = transferAttributes(outGDB,spatialRef,attributeTransferFile,intersectMem)
            if intersectCalc[0] == 'Error':
                return intersectCalc
        # if the transfer succeeds then calculate maskedarea and waternulls   
        # if there are nulls then set them to 0
        nullLyr = os.path.basename(inFCG) + "_null_lyr"
        arcpy.MakeFeatureLayer_management(intersectMem,nullLyr,"WATERAREAKM IS NULL")
        if int(arcpy.GetCount_management(nullLyr)[0])>0:
            arcpy.CalculateField_management(nullLyr,"WATERAREAKM",0, "PYTHON")
        arcpy.CalculateField_management(intersectMem,"MASKEDAREAKM",'!AREAKM! - !WATERAREAKM!','PYTHON')
        # if there are negatives then set them to 0
        negLyr = os.path.basename(inFCG) + "_neg_lyr"
        arcpy.MakeFeatureLayer_management(intersectMem,negLyr,"MASKEDAREAKM <> AREAKM AND MASKEDAREAKM < 0.001")
        if int(arcpy.GetCount_management(negLyr)[0])>0:
            arcpy.CalculateField_management(negLyr,"MASKEDAREAKM",0,"PYTHON")
        # create a summary table in memory
        memSumTbl = 'in_memory' + os.sep + os.path.basename(inFCG) + "_densities"
        try:
            statsFields = [["AREAKM","SUM"],["WATERAREAKM","SUM"],["MASKEDAREAKM","SUM"]]
            arcpy.Statistics_analysis(intersectMem,memSumTbl,statsFields,"UBID")
        except:
            return "Error in " + rootName + " : making table views " + str(arcpy.GetMessages())
        # transfer the values in inFCG
        # read calculation into dictionary
        searchFields = ["UBID","SUM_AREAKM","SUM_WATERAREAKM","SUM_MASKEDAREAKM"]
        try:
            # read the values
            values = {}
            with arcpy.da.SearchCursor(memSumTbl,searchFields) as rows:
                for row in rows:
                    # store with UBID as key and a tuple of numbers as value
                    key = row[0]
                    value = row
                    values[key] = value
        except:
            return ('Error',': Creating Value Dictionary for ' + memSumTbl)
        # write the values to inFCG
        updateFields = ["UBID","AREAKM","WATERAREAKM","MASKEDAREAKM"]
        try:
            with arcpy.da.UpdateCursor(inFCG,updateFields) as rows:
                for row in rows:
                    # grab the id
                    uid = row[0]
                    if uid in values:
                        row[1] = values[uid][1]
                        row[2] = values[uid][2]
                        row[3] = values[uid][3]
                    else:
                        row[1] = 0
                        row[2] = 0
                        row[3] = 0
                    # update the row
                    rows.updateRow(row)
        except:
            return ('Error',': Writing Values from Dictionary for ' + inFCG)

        # write the output to disk
        intersectOut = intersectMem.replace('in_memory',outGDB)
        arcpy.CopyFeatures_management(intersectMem,intersectOut)
        outFCG = outGDB + os.sep + os.path.basename(inFC) + "_gridding"
        arcpy.CopyFeatures_management(inFCG,outFCG)
        # compact the file gdb to save space and improve performance
        arcpy.Compact_management(outGDB)
        return "Processed "+ outGDB + " " + str(datetime.datetime.now()-processTime)
    except:
        return "Error while processing " + outGDB + " " + str(datetime.datetime.now()-processTime) + " " + arcpy.GetMessages()
    
 

def main():
    host = socket.gethostname()
    if host == 'Devsedarc3':
        workspace = r'F:\gpw\release_4_1\process'
    elif host == 'Devsedarc4':
        workspace = r'D:\gpw\release_4_1\process'
    arcpy.env.workspace = workspace
    print "processing"
    procList = arcpy.ListWorkspaces("deu.gdb")
    print procList
    # must create procList
    pool = multiprocessing.Pool(processes=1,maxtasksperchild=1)
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
