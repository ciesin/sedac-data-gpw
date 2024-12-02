# this script reads <iso>_fishnet_processed and
# produces FGDB's and GeoTiffs of CNTM variables
import arcpy, os, datetime, multiprocessing

def grid(gdb):
    arcpy.env.overwriteOutput = True
    startTime = datetime.datetime.now()
    iso = os.path.basename(gdb)[:3]
    rootName = os.path.basename(gdb)[:-12]
    # parse the paths
    outGDB = gdb.replace("fishnets",r"rasters\fgdb").replace("_fishnet.gdb",".gdb")
    outFolder = gdb.replace("fishnets",r"rasters\geotiffs").replace("_fishnet.gdb","")
    # create the output gdb and folder
    try:
        if not arcpy.Exists(outGDB):
            arcpy.CreateFileGDB_management(gdb.replace("fishnets",r"rasters\fgdb").replace(rootName + "_fishnet.gdb",""),rootName)
        else:
            return outGDB + " is already processed"
    except:
        return "Cannot create FGDB: " + outGDB
##    try:
##        if not arcpy.Exists(outFolder):
##            os.mkdir(outFolder)
##    except:
##        return "Cannot create Folder: " + outFolder 
    try:
        arcpy.env.workspace = gdb
        # grab the fishnet
        fishnet = arcpy.ListFeatureClasses("*_fishnet_processed")[0]
        # generate list of variables to grid
        # hard code the area variables
        gridFields = ["NUMINPUTS","MEAN_ADMINAREAKMMASKED","WATERAREAKM","AREAKMMASKED"]
        variableFields = arcpy.ListFields(fishnet,"*CNTM")
        [gridFields.append(variable.name) for variable in variableFields]
        # create FGDB raster
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
            # create FGDB grid
            print gridField
            outGrid = outGDB + os.sep + rootName.upper() + "_" + gridField            
            try:
                arcpy.PolygonToRaster_conversion(fishnet,gridField,outGrid,'CELL_CENTER','#',cellSize)
            except:
                return "Error creating FGDB Grid for: " + rootName + " : " + gridField + " : " + str(arcpy.GetMessages())
##            # create geotiff
##            outTif = outFolder + os.sep + rootName.upper() + "_" + gridField + ".tif"
##            try:
##                arcpy.CopyRaster_management(outGrid,outTif,"#","#",
##                                            -407649103380480.000000,
##                                            "NONE","NONE","32_BIT_FLOAT")
##            except:
##                return "Error creating FGDB Grid for: " + rootName + " : " + gridField + " : " + str(arcpy.GetMessages())
                       
        # success
        return "Created grids for " + rootName + ": " + str(datetime.datetime.now()-startTime)
    except:
        return rootName + " error: " + str(arcpy.GetMessages())
    

def main():
    scriptTime = datetime.datetime.now()
    # set workspaces and preprocess to attach paths
    inWS = r'D:\gpw\stage\fishnets'
    #r'\\Dataserver0\gpw\GPW4\Release_4_0\Prod\Gridding\country\pop_tables'
    arcpy.env.workspace = inWS
    workspaces = arcpy.ListWorkspaces("*")
    workspaces.sort()
    gdb_list = []
    for workspace in workspaces:        
        # describe the workspace
        workDesc = arcpy.Describe(workspace)
        # if it is "BRA, CAN, GRL, RUS, or USA" then it is nested in subfolder
        if str(workDesc.workspaceType)=="FileSystem":
            workspace = workspace + os.sep + 'tiles'
            if workspace ==r'D:\gpw\stage\fishnets\bra\tiles':
                continue
            elif workspace ==r'D:\gpw\stage\fishnets\rus\tiles':
                continue
            elif workspace ==r'D:\gpw\stage\fishnets\grl\tiles':
                continue
            arcpy.env.workspace = workspace
            gdbs = arcpy.ListWorkspaces("*")
            for gdb in gdbs:
                gdb_list.append(gdb)
        else:
            gdb_list.append(workspace)
    print len(gdb_list)
    gdb_list.sort(reverse=True)
##    for gdb in gdb_list:
##        print gdb
##        print grid(gdb)
    # multiprocess the data
    pool = multiprocessing.Pool(processes=22,maxtasksperchild=1)
    print pool.map(grid, gdb_list) 
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()
    print "Script complete"
    print str(datetime.datetime.now()-scriptTime)

if __name__ == '__main__':
    main()
