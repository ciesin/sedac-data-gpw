# summarize count rasters
# Kytt MacManus
# create a summary table of count raster estimates

import arcpy, os, datetime, multiprocessing, csv, sys

def summarizeVectors(params):
    fc = params[0]
    if fc.split("_")[-1]=='processed':
        fileName = 'fishnet'
    else:
        fileName = 'estimates table'
    if params[1]==1:
        # generate the summaryFields
        statsFields = [["MASKEDAREAKM","SUM"]]
    else:
        statsFields = [["MASKEDADMINAREA","SUM"]]
    # list the fields
    fields = arcpy.ListFields(fc,"*2010*CNT*")
    [statsFields.append([field.name,"SUM"]) for field in fields]
    # create a summary table in memory
    memSumTbl = r'in_memory'+ os.sep + os.path.basename(fc) + "_summary"
    arcpy.Statistics_analysis(fc,memSumTbl,statsFields)
    # grab the pop value
    returnList = []
    with arcpy.da.SearchCursor(memSumTbl,"*") as rows:
        for row in rows:
            for index, value in enumerate(row):
                if index < 2:
                    continue
                else:
                    returnList.append(((fileName,statsFields[index-2][0]),value))
    return returnList    
def summarizeRasters(params):
    rasters = params[0]
    rootName = params[1].upper()+"_"
    # define zone raster
    zoneRaster = r'D:\gpw\ancillary\gpw4_extent.tif'
    returnList = []
    for raster in rasters:
        # calculate a zonal statistics in memory
        zonalStat = "in_memory" + os.sep + os.path.basename(raster)
        arcpy.sa.ZonalStatisticsAsTable(zoneRaster,"Value",raster,zonalStat,
                                        "DATA","SUM")
        # grab the pop value
        with arcpy.da.SearchCursor(zonalStat,"SUM") as rows:
            for row in rows:
                value = row[0]
        rasName = os.path.basename(raster)
        rasName = rasName.replace("_CNTM.tif","")
        dirName = os.path.basename(os.path.dirname(raster)).upper()
        variableName = rasName.replace(rootName,"")
        returnList.append((('raster',variableName),value))                    
    return returnList
def process(gdb):
    processTime = datetime.datetime.now()
    arcpy.env.overwriteOutput = True
    arcpy.CheckOutExtension('SPATIAL')
    rootName = os.path.basename(gdb)[:-4]
    # grab the estimates table
    arcpy.env.workspace = gdb
    estimates = os.path.join(gdb,arcpy.ListTables("*estimates")[0])
    # grab the process fishnet
    fishnet = os.path.join(gdb,arcpy.ListFeatureClasses("*processed")[0])
    # grab the rasters
    rootSplit = rootName.split("_")
    if len(rootSplit)>1:
        rasterFolder = r'D:\gpw\release_4_1\country_tifs' + os.sep + rootSplit[0][:3] + os.sep + rootName
    elif len(rootSplit[0]) == 3:
        rasterFolder = r'D:\gpw\release_4_1\country_tifs' + os.sep + rootName
    else:
        rasterFolder = r'D:\gpw\release_4_1\country_tifs' + os.sep + rootSplit[0][:3] + os.sep + rootName
    arcpy.env.workspace = rasterFolder
    rasters = arcpy.ListRasters("*2010*cnt*")
##    return (rasterFolder, rasters)
    rasterList = [os.path.join(rasterFolder,raster) for raster in rasters]
    # perform the calculations
    rasterResults = summarizeRasters((rasters,rootName))
    estimatesResults = summarizeVectors((estimates,0))
    fishnetResults = summarizeVectors((fishnet,1))
    return (rootName,rasterResults,estimatesResults,fishnetResults)
def main():
    scriptTime = datetime.datetime.now()
    # set workspaces and preprocess to attach paths
    workspace = r'D:\gpw\release_4_1\process'
    arcpy.env.workspace = workspace
    gdbs = arcpy.ListWorkspaces('*',"FILEGDB")
    procList = [os.path.join(workspace,gdb) for gdb in gdbs]
    print "processing"
    print procList
     # create multi-process pool and execute tool
    pool = multiprocessing.Pool(processes=20,maxtasksperchild=1)
    results = pool.map(process, procList)
##    print results
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()
##    sys.exit()
    # write to csv
    templateFile = r'D:\gpw\release_4_1' + os.sep + "validation_5_11_17.csv"
    templateCSV = csv.writer(open(templateFile,'wb'))
    templateCSV.writerow(('geography','file','variable','value'))
    for result in results:
        rootName = result[0]
        rasterResults = result[1]
        estimatesResults = result[2]
        fishnetResults = result[3]
        resultsSets = [rasterResults,estimatesResults,fishnetResults]
        for resultsSet in resultsSets:
            for row in resultsSet:
                fileName = row[0][0]
                variableName = row[0][1]
                if resultsSet == fishnetResults:
                    variableName = variableName[:-5]
                value = row[1]
                templateCSV.writerow((rootName,fileName,variableName,value))
    del templateCSV
    print "Script Complete: " + str(datetime.datetime.now()-scriptTime)
if __name__ == '__main__':
    main()
