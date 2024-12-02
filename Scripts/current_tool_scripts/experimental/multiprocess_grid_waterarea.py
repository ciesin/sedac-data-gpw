# Kytt MacManus
# 4-25-14

# import libraries
import os, arcpy, sys, csv
import datetime
import multiprocessing
#,csvFile):
def grid(outWS):
    # Define inputs
    # Input ISOCODE
    fcString = os.path.basename(outWS)[:-4]
    fcString = fcString.upper()
    print fcString
    # Create Output Folder
    wsRoot = outWS.replace(os.path.basename(outWS),"")
    outputRoot = wsRoot.replace("inputs","rasters")
    outGDB = fcString.lower() + "_grids"
    outputFolder = outputRoot + outGDB + ".gdb" 
    # Define Workspace
    arcpy.env.workspace = outputFolder
    # Project Data
    # Input Fishnet
    fish = outWS + os.path.sep + fcString + "_fishnet"
    # Coordinate System
    wgs84 = arcpy.SpatialReference(4326)

    # Define Gridding Variables
    gridFieldsWildCard = "*WATERAREA*"#
    gridFields = arcpy.ListFields(fish,gridFieldsWildCard)

    # Lines per degree, determines the output resolution 120 = 30 arc-seconds resolution
    # 1 degree divided into 120 parts is 30 seconds
    linespd = 120## Update As Needed
    cellSize = 1.0 / linespd
    # Output the gridded count rasters
    for field in gridFields:
        gridField = field.name
        gridName = fcString.upper() + "_" + gridField[4:]
        print "The field to be gridded is " + gridField
        arcpy.AddMessage("The field to be gridded is " + gridField)
        
        # Describe Fish
        desc = arcpy.Describe(fish)
        # Calculate Raster Extent
        extent = desc.Extent
        xmin = int(round(extent.XMin - .5))
        xmax = int(round(extent.XMax + .5))
        ymin = int(round(extent.YMin - .5))
        ymax = int(round(extent.YMax + .5))
        arcpy.env.extent = arcpy.Extent(xmin,ymin,xmax,ymax)
        arcpy.env.outputCoordinateSystem = wgs84
        arcpy.env.cellSize = cellSize
        print "The extent is " + str(arcpy.env.extent)
        arcpy.AddMessage("The extent is " + str(arcpy.env.extent))
        
        # Grid
        outGrid =  outputFolder + os.path.sep + gridName
        print outGrid
        if arcpy.Exists(outGrid):
            arcpy.AddMessage(outGrid + " exists")
            print outGrid + " exists"
        else:
            # Isolate WATER CELLS > 0
            waterLyr = fcString + "_" + gridName + "_lyr"
            try:
                arcpy.MakeFeatureLayer_management(fish,waterLyr,gridField +  '> 0')
            except:
                arcpy.GetMessages()
            features = arcpy.GetCount_management(waterLyr)[0] 
            if features =="0":
                error = ""
##                csvFile.writerow((fcString,outGrid,features,error))
                del features
                print "waterLyr has 0 features, skipping"
            else:
                try:
                    arcpy.PolygonToRaster_conversion(waterLyr,gridField,outGrid,'CELL_CENTER','#',cellSize)
                    print "Created " + outGrid
                    del features
                    arcpy.AddMessage("Created " + outGrid)
                except:
                    error = "Error"
##                    csvFile.writerow((fcString,outGrid,features,error))
                    del features
                    print arcpy.GetMessages()
                    arcpy.AddMessage(arcpy.GetMessages())
    
    
def main():
    # set counter
    startTime = datetime.datetime.now()
    # define workspace
    workspace = r'\\dataserver0\gpw\GPW4\Gridding\country\inputs'
##    workspace = r'\\dataserver0\gpw\GPW4\Gridding\country\inputs\usa_state\test'
    arcpy.env.workspace = workspace
    # list gdbs
    gdbs = arcpy.ListWorkspaces("*","FILEGDB")
    # define csv file
    attributes = r'\\dataserver0\gpw\GPW4\Gridding\validation' + os.sep + "water_11_3_14.csv"
    # open csv file and write header
##    csvFile = csv.writer(open(attributes,'wb'))
##    csvFile.writerow(("ISO","FILE","FEATURES","ERROR"))

##    pool = multiprocessing.Pool(processes=40)
##    pool.map(grid, gdbs) 
##    # Synchronize the main process with the job processes to
##    # ensure proper cleanup.
##    pool.close()
##    pool.join()

    for gdb in gdbs:
        gdbTime = datetime.datetime.now()
        print gdb
        numProc = 1
        pool = multiprocessing.Pool(processes=numProc)
        pool.map(grid, [gdb]) 
        # Synchronize the main process with the job processes to
        # ensure proper cleanup.
        pool.close()
        pool.join()
        print "Processed " + gdb
        print datetime.datetime.now() - gdbTime
##        # define output workspace
##        outWS = gdb
##        grid(outWS,csvFile)
##        print datetime.datetime.now() - gdbTime
            
    print datetime.datetime.now() - startTime
if __name__ == '__main__':
    main()


        
        
