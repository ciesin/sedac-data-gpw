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
    arcpy.env.overwriteOutput = True
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
        # grab the fishnet
        arcpy.env.workspace = outGDB
        fishnet = arcpy.ListFeatureClasses("*fishnet")[0]
        # add and calculate fields
        arcpy.AddField_management(fishnet,"PIXELID","LONG")
        arcpy.CalculateField_management(fishnet,"PIXELID",
                                        "!gridcode!","PYTHON")
        arcpy.AddField_management(fishnet,"PIXELAREA","DOUBLE")
        # project the fishnet
        projFish = fishnet + "_mollweide"
        arcpy.Project_management(fishnet,projFish,spatialRef)
        arcpy.CalculateField_management(projFish,"PIXELAREA",'!shape.area@SQUAREKILOMETERS!','PYTHON')
        searchFields = ["PIXELID","PIXELAREA"]
        try:
            # read the values
            values = {}
            with arcpy.da.SearchCursor(projFish,searchFields) as rows:
                for row in rows:
                    # store with UBID as key and a tuple of numbers as value
                    key = row[0]
                    value = row[1]
                    values[key] = value
        except:
            return ('Error',': Creating Value Dictionary for ' + projFish)
        # write the values to inFCG
        updateFields = ["PIXELID","PIXELAREA"]
        try:
            with arcpy.da.UpdateCursor(fishnet,updateFields) as rows:
                for row in rows:
                    # grab the id
                    uid = row[0]
                    if uid in values:
                        row[1] = values[uid]
                        
                    else:
                        row[1] = 0
                    # update the row
                    rows.updateRow(row)
        except:
            return ('Error',': Writing Values from Dictionary for ' + fishnet)

        # compact the file gdb to save space and improve performance
        arcpy.Delete_management(projFish)
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
    procList = arcpy.ListWorkspaces("*")
    print procList
    # must create procList
    pool = multiprocessing.Pool(processes=15,maxtasksperchild=1)
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
