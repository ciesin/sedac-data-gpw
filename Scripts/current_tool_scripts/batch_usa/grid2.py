# Kytt MacManus
# 4-25-14

# import libraries
import os, arcpy, sys
import datetime
import multiprocessing

def grid(outWS):
    # Define inputs
    # Input ISOCODE
    fcString = os.path.basename(outWS)[:-4]
    fcString = fcString.upper()
    print fcString
    # Create Output Folder
    wsRoot = outWS.replace(os.path.basename(outWS),"")
    outputRoot = wsRoot.replace("states","rasters")
    outGDB = fcString.lower() + "_grids"
    outputFolder = outputRoot + outGDB + ".gdb"
    print outputFolder
    if not arcpy.Exists(outputFolder):
        arcpy.CreateFileGDB_management(outputRoot,outGDB)
        print "Created " + outputFolder
        arcpy.AddMessage("Created " + outputFolder)
    else:
        arcpy.AddMessage(outputFolder + " already exists")
    # Define Workspace
    arcpy.env.workspace = outputFolder
    # Project Data
    # Input Fishnet
    fish = outWS + os.path.sep + fcString + "_fishnet"
    # Coordinate System
    wgs84 = arcpy.SpatialReference(4326)
    # Describe Fish
    desc = arcpy.Describe(fish)
    # Calculate Raster Extent
    extent = desc.Extent
    xmin = int(round(extent.XMin - .5))
    xmax = int(round(extent.XMax + .5))
    ymin = int(round(extent.YMin - .5))
    ymax = int(round(extent.YMax + .5))

    # Define Gridding Variables
    gridFieldsWildCard = "*CNTM"#
    gridFields = arcpy.ListFields(fish,gridFieldsWildCard)

    # Lines per degree, determines the output resolution 120 = 30 arc-seconds resolution
    # 1 degree divided into 120 parts is 30 seconds
    linespd = 120 ## Update As Needed
    cellSize = 1.0 / linespd
    # Output the gridded count rasters
    for field in gridFields:
        gridField = field.name
        print "The field to be gridded is " + gridField
        arcpy.AddMessage("The field to be gridded is " + gridField)
        # Output Grids
        #+ os.path.sep + fcString + "_grids.gdb"
        if gridField[:3] == "SUM":
            gridName = gridField[4:]
        else:
            gridName = gridField
        outAreaGrid = outputFolder + os.path.sep + fcString + "_AREA" 
        outPopGrid =  outputFolder + os.path.sep + fcString + "_" + gridName
        arcpy.env.extent = arcpy.Extent(xmin,ymin,xmax,ymax)
        arcpy.env.outputCoordinateSystem = wgs84
        arcpy.env.cellSize = cellSize
        print "The extent is " + str(arcpy.env.extent)
        arcpy.AddMessage("The extent is " + str(arcpy.env.extent))
        if arcpy.Exists(outAreaGrid):
            pass
        else:
            try:
                arcpy.PolygonToRaster_conversion(fish,"SUM_AREAKMMASKED",outAreaGrid,'CELL_CENTER','#',cellSize)
                print "Created " + outAreaGrid
                arcpy.AddMessage("Created " + outAreaGrid)
            except:
                print arcpy.GetMessages()
                arcpy.AddMessage(arcpy.GetMessages())
        if arcpy.Exists(outPopGrid):
            arcpy.AddMessage(outPopGrid + " exists")
        else:
            try:
                arcpy.PolygonToRaster_conversion(fish,gridField,outPopGrid,'CELL_CENTER','#',cellSize)
                print "Created " + outPopGrid
                arcpy.AddMessage("Created " + outPopGrid)
            except:
                print arcpy.GetMessages()
                arcpy.AddMessage(arcpy.GetMessages())
    
    
def main():
    # set counter
    startTime = datetime.datetime.now()
    # define workspace
    workspace = r'D:\gpw\usa_state\states'
##    workspace = r'\\dataserver0\gpw\GPW4\Gridding\country\inputs\usa_state\test'
    arcpy.env.workspace = workspace
    # list gdbs
    gdbs = arcpy.ListWorkspaces("*","FILEGDB")
####    gdbList = []
####    for gdb in gdbs:
####        checkFile = gdb + os.sep + os.path.basename(gdb)[:-4] + "_gridding"
####        if arcpy.Exists(checkFile):
####            pass
####        else:
####            gdbList.append(gdb)
####            print gdb
####            grid(gdb)
    pool = multiprocessing.Pool(processes=12,maxtasksperchild=1)
    pool.map(grid, gdbs) 
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()

##    for gdb in gdbs:
##        print gdb
##        # define output workspace
##        outWS = gdb
##        grid(outWS)            
            
    print datetime.datetime.now() - startTime
if __name__ == '__main__':
    main()


        
        
