# summarize count rasters
# Kytt MacManus
# create a summary table of count raster estimates

import arcpy, os, datetime, multiprocessing

def summarizeRasters(gdb):
    processTime = datetime.datetime.now()
    arcpy.env.overwriteOutput = True
    arcpy.CheckOutExtension('SPATIAL')
    iso = os.path.basename(gdb)[:-4].upper()
    # define zone raster
    zoneRaster = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\global\ancillary\gpw4_extent.tif'
    # define schema table
    schemaTable = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\schema_tables.gdb\count_raster_summary'
    # set workspace
    arcpy.env.workspace = gdb
    # list totpop rasters
    rasters = arcpy.ListRasters("*ATOTPOP*")
    if len(rasters)==0:
        return gdb + " has no rasters"
    # create a copy of the schema table
    summaryTable = gdb + os.sep + iso + "_count_raster_summary"
    try:
        arcpy.CopyRows_management(schemaTable,summaryTable)
        # iterate the rasters
        i = 0
        for raster in rasters:
            print raster[4:-5]
            year = raster.split("_")[3]
            # calculate a zonal statistics in memory
            zonalStat = "in_memory" + os.sep + iso + "_" + raster
            arcpy.sa.ZonalStatisticsAsTable(zoneRaster,"Value",raster,zonalStat,
                                            "DATA","SUM")
            # grab the pop value
            with arcpy.da.SearchCursor(zonalStat,"SUM") as rows:
                for row in rows:
                    popValue = row[0]
                    print iso
                    print popValue
            # add the value to the summaryTable
            # if it is the first iteration insert,
            # otherwise update
            if i == 0:
                i = 1
                cursor = arcpy.InsertCursor(summaryTable)
                row = cursor.newRow()
                row.setValue("ISO",iso)
                row.setValue(raster[4:-5],popValue)
                cursor.insertRow(row)                
                del cursor
                del row
            else:
                with arcpy.da.UpdateCursor(summaryTable,[raster[4:-5]]) as cursor:
                    for row in cursor:
                        row[0] = popValue
                        cursor.updateRow(row)
                        print "updated row"
        # return success
        return 1
                
    except:
        return "Error: " + gdb + " " + str(arcpy.GetMessages())
        

def main():
    # set workspaces and preprocess to attach paths
    workspace = r'Z:\GPW4\Beta\Gridding\rasters\rus'
    workspaces = [workspace]
    gdb_list = []
    for ws in workspaces:
        arcpy.env.workspace = ws
        gdbs = arcpy.ListWorkspaces('*',"FILEGDB")
        gdbs.sort()
        gdb_temp = [os.path.join(ws, gdb) for gdb in gdbs]
        for gdbt in gdb_temp:
            gdb_list.append(gdbt)    
       
    print "processing"
    print len(gdb_list)
##    for gdb in gdb_list:
##        summarizeRasters(gdb)
    # create multi-process pool and execute tool
    pool = multiprocessing.Pool(processes=1,maxtasksperchild=1)
    results = pool.map(summarizeRasters, gdb_list)
    print(results)
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()

if __name__ == '__main__':
    main()
