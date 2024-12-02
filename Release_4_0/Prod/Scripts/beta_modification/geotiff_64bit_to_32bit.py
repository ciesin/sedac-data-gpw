# Kytt MacManus
# March 21 2014
# Convert GPW FGDB Grids to GeoTiff

# Import libraries
import arcpy, os, datetime, multiprocessing

def process(grid):
    procTime = datetime.datetime.now()
    print "Processing " + grid
    # name of output directory
    workDir = os.path.dirname(grid)
    datasetName = os.path.basename(grid)[:-9]
    outputDir = workDir + os.sep + datasetName
    # copy grid to geotiff
    outTif = outputDir + os.sep + os.path.basename(grid)
    if arcpy.Exists(outTif):
        return outTif + " already exists"
    else:
        try:
            arcpy.CopyRaster_management(grid,outTif,"#","#",
                                        -407649103380480.000000,
                                        "NONE","NONE","32_BIT_FLOAT")
            return "Created " + outTif + " : " + str(datetime.datetime.now()-procTime)
        except:
            return arcpy.GetMessages()
def main():
    scriptTime = datetime.datetime.now()
    # Define workspace
    gdb = r'D:\gpw\4_0_prod\outTifs'
    # Set workspace environment
    arcpy.env.workspace = gdb
    # list grids
    grids = arcpy.ListRasters("*_water*")
    grid_list = [os.path.join(gdb, grid) for grid in grids]
    print len(grids)
##    for grid in grid_list:
##        process(grid)
##        break
    # create multi-process pool and execute tool
    pool = multiprocessing.Pool(processes=1,maxtasksperchild=1)
    results = pool.map(process, grid_list)
    print(results)
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()
    print "Script complete"
    print str(datetime.datetime.now()-scriptTime)

if __name__ == '__main__':
    main()
                
