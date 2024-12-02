# this script reads <iso>_fishnet_processed and
# produces FGDB's and GeoTiffs of CNTM variables
import arcpy, os, datetime, multiprocessing

def merge(workspace):
    procTime = datetime.datetime.now()
    arcpy.env.overwriteOutput = True
    arcpy.CheckOutExtension("SPATIAL")
    # define outExtent
    outExtent = r'\\Dataserver0\gpw\GPW4\Release_4_0\Prod\Gridding\global\ancillary\gpw4_extent.tif'
    arcpy.env.extent = outExtent
    startTime = datetime.datetime.now()
    iso = os.path.basename(workspace).upper()
    # parse the paths
    outGDB = r'D:\gpw\stage\rasters\merge' + os.sep + iso.lower() + '.gdb'
    if not arcpy.Exists(outGDB):
        arcpy.CreateFileGDB_management(os.path.dirname(outGDB),iso.lower())
    try:
        # set workspace
        arcpy.env.workspace = workspace
        # list gdbs
        gdbs = arcpy.ListWorkspaces("*","FILEGDB")
        for gdb in gdbs:
            arcpy.env.workspace = gdb
            # list variables to grid
            varIDS = arcpy.ListRasters("*")
            # post process to remove the rootname
            rootName = os.path.basename(gdb)[:-4]
            varIDS = [variable[len(rootName):] for variable in varIDS]
            break
        meanArea = "_MEAN_ADMINAREAKMMASKED"
        for varID in varIDS:
            gridRasters = [os.path.join(gdb, os.path.basename(gdb)[:-4].upper() + varID) for gdb in gdbs]
            outRaster = outGDB + os.sep + iso + varID
            if not arcpy.Exists(outRaster):                
                if varID == meanArea:
                    cellStats = arcpy.sa.CellStatistics(gridRasters, "MEAN", "DATA")
                else:
                    cellStats = arcpy.sa.CellStatistics(gridRasters, "SUM", "DATA")
                cellStats.save(outRaster)
                del cellStats
                arcpy.BuildPyramidsandStatistics_management(outRaster)
                    
        return iso + " processed: " + str(datetime.datetime.now()-procTime)
    except:
        return iso + " error: " + str(arcpy.GetMessages())
    
def main():
    scriptTime = datetime.datetime.now()
    # set workspaces and preprocess to attach paths
    inWS = r'D:\gpw\stage\rasters\merge'
    arcpy.env.workspace = inWS
    workspaces = arcpy.ListWorkspaces("bra*","Folder")
    workspaces.sort()
##    print merge(workspaces[0])
    # multiprocess the data
    pool = multiprocessing.Pool(processes=1,maxtasksperchild=1)
    print pool.map(merge, workspaces) 
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()
    print "Script complete"
    print str(datetime.datetime.now()-scriptTime)

if __name__ == '__main__':
    main()
