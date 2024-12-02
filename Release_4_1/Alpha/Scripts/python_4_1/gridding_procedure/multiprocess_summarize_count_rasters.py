# summarize count rasters
# Kytt MacManus
# create a summary table of count raster estimates

import arcpy, os, datetime, multiprocessing, csv

def summarizeRasters(raster):
    processTime = datetime.datetime.now()
    arcpy.env.overwriteOutput = True
    arcpy.CheckOutExtension('SPATIAL')
    # define zone raster
    zoneRaster = r'D:\gpw\ancillary\gpw4_extent.tif'
    # create a copy of the schema table
    split = os.path.basename(raster).split("_")
    if len(split)==6:
        variable = split[3]
        year = split[4]
    elif len(split)==7:
        variable = split[3]+"-"+split[4]
        year = split[5]
    else:
        variable = split[2]
        year = "N/A"
    try:
        # calculate a zonal statistics in memory
        zonalStat = "in_memory" + os.sep + os.path.basename(raster)
        arcpy.sa.ZonalStatisticsAsTable(zoneRaster,"Value",raster,zonalStat,
                                        "DATA","SUM")
        # grab the pop value
        with arcpy.da.SearchCursor(zonalStat,"SUM") as rows:
            for row in rows:
                value = row[0]

        return(variable,year,value)                
    except:
        return "Error: " + gdb + " " + str(arcpy.GetMessages())
        
def main():
    scriptTime = datetime.datetime.now()
    # set workspaces and preprocess to attach paths
    workspace = r'D:\gpw\release_4_1\merge'
    arcpy.env.workspace = workspace
    rasters = arcpy.ListRasters('*cntm*')+arcpy.ListRasters('*area*')
    procList = [os.path.join(workspace,raster) for raster in rasters]
    print "processing"
    print procList
     # create multi-process pool and execute tool
    pool = multiprocessing.Pool(processes=40,maxtasksperchild=1)
    results = pool.map(summarizeRasters, procList)
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()
    # write to csv
    templateFile = r'D:\gpw\release_4_1' + os.sep + "raster_summaries_5_11_17.csv"
    templateCSV = csv.writer(open(templateFile,'wb'))
    templateCSV.writerow(('variable','year','value'))
    for result in results:
        templateCSV.writerow((result[0],result[1],int(result[2])))
    del templateCSV
    print "Script Complete: " + str(datetime.datetime.now()-scriptTime)
if __name__ == '__main__':
    main()
