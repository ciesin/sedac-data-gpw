# multiprocess template
import os, datetime, socket
import multiprocessing
import arcpy
scriptTime = datetime.datetime.now()
def correctMeanArea(fishnet):
    expression = "WATERAREAKM >0 AND MEAN_MASKEDADMINAREA IS NULL"
    nullLyr = os.path.basename(fishnet) + "_lyr"
    arcpy.MakeFeatureLayer_management(fishnet,nullLyr,expression)
    arcpy.CalculateField_management(nullLyr,"MEAN_MASKEDADMINAREA",0,"PYTHON")
    return
def tableToDict(table,searchFields):
    values = {}
    # read the values
    with arcpy.da.SearchCursor(table,searchFields) as rows:
        for row in rows:
            # store with UBID as key and a tuple of numbers as value
            key = row[0]
            value = row
            values[key] = value
    return values
    
def process(outGDB):
    arcpy.env.overwriteOutput=True
    arcpy.env.compression = "LZW"
    processTime = datetime.datetime.now()
    iso = os.path.basename(outGDB)[:3]
    rootName = os.path.basename(outGDB)[:-4]
    inWS = os.path.dirname(outGDB)
    outWS = inWS.replace(os.path.basename(inWS),'country_tifs')
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
    try:
        arcpy.env.workspace = outGDB
        fishnets = arcpy.ListFeatureClasses("*processed")
        if len(fishnets)==0:
            return outGDB + " fishnet is missing"
        fishnet = fishnets[0]
        # function to fill in zeroes for mean admin area where waterarea > 0
        correctMeanArea(fishnet)
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
        gridFields = ["NUMINPUTS","CONTEXT"]
        fields = arcpy.ListFields(fishnet,"*AREA*")+arcpy.ListFields(fishnet,"*CNTM")
        for field in fields:
            if field.name == "Shape_Area":
                continue
            gridFields.append(field.name)
        for gridField in gridFields:
            outGrid = outFolder + os.sep + rootName.upper() + "_" + gridField + ".tif"           
            if not arcpy.Exists(outGrid):
                try:
                    arcpy.env.compression = 'LZW'
                    arcpy.PolygonToRaster_conversion(fishnet,gridField,outGrid,'CELL_CENTER','#',cellSize)
                except:
                    return "Error creating Grid for: " + rootName + " : " + gridField + " : " + str(arcpy.GetMessages())
        
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
    # must create procList
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
