import os
import multiprocessing
import arcpy
from arcpy import env
import datetime

# set counter
startTime = datetime.datetime.now()

def merge(raster):
    # Check out Spatial Analyst
    arcpy.CheckOutExtension("SPATIAL")
    # Parse WildCard
    wildCard = "*" + raster[10:]
    # define workspace
    workspace = r'E:\gpw\usa_state\rasters'
    arcpy.env.workspace = workspace
    # list GDBS
    gdbs = arcpy.ListWorkspaces("*", "FileGDB")
    # create list object
    cellList = []
    for gdb in gdbs:
##        print gdb
        arcpy.env.workspace = gdb 
        # grab the necessary file and append
        grids = arcpy.ListRasters(wildCard)
        appendRaster = gdb + os.sep + grids[0]
        cellList.append(appendRaster)    
##    print cellList
    # Set Cell Size        
    arcpy.env.cellSize = raster
    # Set extent
    # First calculate the extent
    outExtent = r'E:\gpw\usa_state\usa_extent\us_extent.tif'    
    # Set Extent Environment
    arcpy.env.extent = outExtent
    # Define output File
    outCellStats = r'E:\gpw\usa_state\usa_grids' + os.sep + "USA" + raster[10:] + ".tif"
    if not arcpy.Exists(outCellStats):
        print "Cell Stats Processing"
        try:
            cellStats = arcpy.sa.CellStatistics(cellList, "SUM", "DATA")
            print "created in memory"
            cellStats.save(outCellStats)
##            del cellStats
            print "Created " + outCellStats
        except:
            print arcpy.GetMessages()



def main():
    # set counter
    startTime = datetime.datetime.now()
    # define workspace
    workspace = r'E:\gpw\usa_state\rasters'
    rasterWS = workspace + os.sep + 'usa_akeast_grids.gdb'
    arcpy.env.workspace = rasterWS
    # List Rasters
    rasters = arcpy.ListRasters("*NUMINPUTS")
##    pool = multiprocessing.Pool(processes=15)#,maxtasksperchild=1)
##    pool.map(merge, rasters) 
##    # Synchronize the main process with the job processes to
##    # ensure proper cleanup.
##    pool.close()
##    pool.join()

    for raster in rasters:
        print raster
        # define output workspace
        merge(raster)            
            
    print datetime.datetime.now() - startTime
if __name__ == '__main__':
    main()
 
