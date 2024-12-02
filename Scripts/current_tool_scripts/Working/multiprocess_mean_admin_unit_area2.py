# Kytt MacManus
# April 14 2014
# Produce Mean Area Unit Grids

##  From GPW3 Documentation:
##    Because countries vary between each other and internally on the size of the
##    administrative areas, analysis of the data may benefit from more information about the
##    administrative area underlying each unit in the output grid. Thus, for GPW version 3 we
##    constructed a population-weighted administrative unit area layer. This layer allows the
##    determination, on a pixel-by-pixel basis, of the mean administrative unit area that was
##    used as an input for the population count and density grids. For grid cells (pixels) that
##    are wholly comprised of one input unit, the output value is the total area of the input
##    unit. Where grid cells are comprised of multiple input units, the output value is the
##    population-weighted mean of all of the inputs.


# Import libraries
import arcpy, os, sys, datetime, multiprocessing

def meanArea(gdb):
    # Check out Spatial Analyst License
    arcpy.CheckOutExtension("SPATIAL")
    # Define pixel id
    pixelID = "PIXELID"
   
    # parse iso code
    iso = os.path.basename(gdb)[:-4]
    # define outputs
    outGDB = gdb.replace("inputs","rasters")[:-4] + "_grids.gdb"
    outInputs = outGDB + os.path.sep + iso.upper() + "_NUMINPUTS" 
    meanUnits = outGDB + os.path.sep + iso.upper() + "_MEAN_ADMIN_UNIT_AREA"
    scratchGDB = r'\\dataserver0\gpw\GPW4\Gridding\country\rasters\scratch\meanArea' + os.sep + iso + ".gdb"
    # check if scratchGDB exists, if not then create it
    if not arcpy.Exists(scratchGDB):
        try:
            arcpy.CreateFileGDB_management(r'\\dataserver0\gpw\GPW4\Gridding\country\rasters\scratch\meanArea',iso)
            print "Created scratchGDB for " + iso
        except:
            print arcpy.GetMessages()
    else:
        print "The scratch gdb already exists"
    arcpy.env.scratchWorkspace = scratchGDB
    # check if the country is already complete
    if arcpy.Exists(meanUnits):
        print meanUnits + " already exists"
    else:
        # change workspace to gdb
        arcpy.env.workspace = gdb
        
        # define input fishnet and check to see if it exists
        inFish = gdb + os.sep + iso + "_fishnet"
        if arcpy.Exists(inFish):
            pass
        else:
            sys.exit("Fishnet is missing, check!")   
        
        # define intersect file
        # check to see if the file is in the GDB, if it is assign it to a
        # variable otherwise kill the script
        # list files ending in fishnet_clipped_intersect
        intList = arcpy.ListFeatureClasses("*fishnet_clipped_intersect")
        if len(intList) == 1:
            intersect = intList[0]
            print intersect
        else:
            sys.exit("Intersect file is missing, check!")

        # Determine which field is present for Admin ATOTPOPBT
    ##    popList = arcpy.ListFields(intersect,"ATOTPOPBT")
    ##    if len(popList) == 1:
    ##        totPop1 = popList[0]
    ##        totPop = totPop1.name
    ##        print totPop
    ##    else:
        ePopList = arcpy.ListFields(intersect,"E_ATOTPOPBT_2010")
        if len(ePopList) == 1:
            totPop1 = ePopList[0]
            totPop = totPop1.name
            print totPop
        else:
            sys.exit("The total administrative unit pop variable is missing, check!")

        # Check that PIXELID is present
        pixList = arcpy.ListFields(intersect,"PIXELID")
        if len(pixList) == 1:
            pass
        else:
            sys.exit("PIXELID variable is missing, check!")
      
        # Add "AREAPOPPRODUCT" and "ATOTPOPBT_ADMIN" field to derive weighting scheme
        try:
            addTime = datetime.datetime.now()
            areaPop = "AREAPOPPRODUCT"
            adminPop = "ATOTPOPBT_ADMIN"
            arcpy.AddField_management(intersect,areaPop,"DOUBLE")
            arcpy.AddField_management(intersect,adminPop,"DOUBLE")
            # also add it to inFish
            arcpy.AddField_management(inFish,"SUM_" + areaPop,"DOUBLE")     
            arcpy.AddField_management(inFish,"SUM_" + adminPop,"DOUBLE")
            arcpy.AddField_management(inFish,"NUMINPUTS","DOUBLE")
            print "Added " + areaPop + " and " + adminPop
            print datetime.datetime.now() - addTime
        except:
            print arcpy.GetMessages()
        
        # Make a feature layer from the intersect file in order to make field calculations fast
        try:
            addTime = datetime.datetime.now()
            intLyr = iso + "_intlyr"
            arcpy.MakeFeatureLayer_management(intersect,intLyr)
            arcpy.CalculateField_management(intLyr,areaPop,"!ADMINAREAKM! * !" + totPop + "!" , "PYTHON")
            arcpy.CalculateField_management(intLyr,adminPop, "!" + totPop + "!" , "PYTHON")
            arcpy.Delete_management(intLyr)
            print "Calculated " + areaPop + " and " + adminPop
            print datetime.datetime.now() - addTime
        except:
            print arcpy.GetMessages()

        # Calculate summary statistics to derive pixel values for input ADMINAREAKM and AREAPOPPRODUCT
        try:
            addTime = datetime.datetime.now()
            # define output file
            sumTbl = gdb + os.sep + iso + "_mean_administrative_unit_area"
            # define fields to sum
            sumFields = [[adminPop,"SUM"],[areaPop,"SUM"]]
            arcpy.Statistics_analysis(intersect,sumTbl,sumFields,pixelID)
            arcpy.AddIndex_management(sumTbl,pixelID,pixelID + "_index","UNIQUE")
            print "Executed summary statistics"
            print datetime.datetime.now() - addTime
        except:
            print arcpy.GetMessages()

        # join results to the original fishnet
        # first check that the fishnet has an index, if not build one
        if not len(arcpy.ListIndexes(inFish,"PIXELID_index"))==1:
            arcpy.AddIndex_management(inFish,pixelID,pixelID + "_index","UNIQUE")
        else:
            pass
        # next perform the join
        try:
            joinTime = datetime.datetime.now()
            # define baseFeature and joinFeature, and joinField
            baseFeature = inFish
            joinFeature = sumTbl
            joinField = pixelID
            # define joinVariables
            joinVariables = ["SUM_" + adminPop, "SUM_" + areaPop]
            # Make Feature Layers
            layer1 = os.path.basename(baseFeature) + "_lyr"
            layer2 = os.path.basename(joinFeature) + "_lyr"
            try:
                addTime = datetime.datetime.now()
                if not arcpy.Exists(layer1):
                    try:
                        arcpy.MakeFeatureLayer_management(baseFeature,layer1)
                    except:
                        arcpy.MakeTableView_management(baseFeature,layer1)
                if not arcpy.Exists(layer2):
                    try:
                        arcpy.MakeFeatureLayer_management(joinFeature,layer2)
                    except:
                        arcpy.MakeTableView_management(joinFeature,layer2)
                print "Made Feature Layers"
                print datetime.datetime.now() - addTime
            except:
                print arcpy.GetMessages()
            # Add Join
            try:
                addTime = datetime.datetime.now()
                arcpy.AddJoin_management(layer1,joinField,layer2,joinField,"KEEP_ALL")
                print "Added Join"
                print datetime.datetime.now() - addTime
            except:
                print arcpy.GetMessages()
            # Transfer fields
            for joinVariable in joinVariables:
                print joinVariable
                try:
                    addTime = datetime.datetime.now()
                    expression = '!' + os.path.basename(joinFeature) + "." + joinVariable + '!'
                    arcpy.CalculateField_management(layer1,os.path.basename(baseFeature) + "." + joinVariable,expression,'PYTHON')
                    print "Calculated " + joinVariable
                    print datetime.datetime.now() - addTime
                except:
                    print arcpy.GetMessages()
            # Transfer Frequency Field
            try:
                addTime = datetime.datetime.now()
                expression = '!' + os.path.basename(joinFeature) + '.FREQUENCY!'
                arcpy.CalculateField_management(layer1,os.path.basename(baseFeature) + ".NUMINPUTS",expression,'PYTHON')
                print "Calculated NUMINPUTS"
                print datetime.datetime.now() - addTime
            except:
                print arcpy.GetMessages()
            try:
                addTime = datetime.datetime.now()
                arcpy.RemoveJoin_management(layer1,os.path.basename(joinFeature))
                print "Removed temporary join"
                arcpy.Delete_management(layer1)
                arcpy.Delete_management(layer2)
                print datetime.datetime.now() - addTime
            except:
                print arcpy.GetMessages()            
            print "Joined Statistic Fields to " + inFish
            print datetime.datetime.now() - joinTime
        except:
            print arcpy.GetMessages()

        # Grid the two new variables, store the rasters in the input gdb as they are input data, not final results
        # Coordinate System
        wgs84 = arcpy.SpatialReference(4326)
        # Describe Fish
        desc = arcpy.Describe(inFish)
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
        # Set environments
        arcpy.env.extent = arcpy.Extent(xmin,ymin,xmax,ymax)
        arcpy.env.outputCoordinateSystem = wgs84
        arcpy.env.cellSize = cellSize
        print "The extent is " + str(arcpy.env.extent)
        # Use polygon to raster to grid each variable  
        try:
            gridTime = datetime.datetime.now()
            outAreaPopGrid = gdb + os.path.sep + iso + "_AREAPOPPRODUCT"
            arcpy.PolygonToRaster_conversion(inFish,"SUM_AREAPOPPRODUCT",outAreaPopGrid,'CELL_CENTER','#',cellSize)
            print "Created " + outAreaPopGrid
            print datetime.datetime.now() - gridTime
        except:
            print arcpy.GetMessages()
        try:
            gridTime = datetime.datetime.now()
            outAdminPopGrid = gdb + os.path.sep + iso + "_ATOTPOPBT_ADMIN" 
            arcpy.PolygonToRaster_conversion(inFish,"SUM_ATOTPOPBT_ADMIN",outAdminPopGrid,'CELL_CENTER','#',cellSize)
            print "Created " + outAdminPopGrid
            print datetime.datetime.now() - gridTime
        except:
            print arcpy.GetMessages()
        try:
            gridTime = datetime.datetime.now()        
            arcpy.PolygonToRaster_conversion(inFish,"NUMINPUTS",outInputs,'CELL_CENTER','#',cellSize)
            print "Created " + outInputs
            print datetime.datetime.now() - gridTime
        except:
            print arcpy.GetMessages()
        # Create Country Level Mean Unit Grid
        try:
            gridTime = datetime.datetime.now()        
            meanUnitArea = arcpy.sa.Divide(outAreaPopGrid,outAdminPopGrid)
            meanUnitArea.save(meanUnits)
            print "Created " + meanUnits
            print datetime.datetime.now() - gridTime
        except:
            print arcpy.GetMessages()

def main():

    runTime = datetime.datetime.now()
    # Define workspace
    workspace = r'\\dataserver0\gpw\GPW4\Gridding\country\inputs'
    # Set workspace environment
    arcpy.env.workspace = workspace
    # define wildcards
    wildcards = ["ko"]
    for wildcard in wildcards:
        proTime = datetime.datetime.now()
        # List File GDBs
        gdbs = arcpy.ListWorkspaces(wildcard + "*","FILEGDB")
        gdbs.sort()
        for gdb in gdbs:
            if gdb == r'\\Dataserver0\gpw\GPW4\Gridding\country\inputs\kir.gdb':
                pass
            else:
                print gdb
    ##            meanArea(gdb)
                numProc = 1
                pool = multiprocessing.Pool(processes=numProc)
                pool.map(meanArea, [gdb]) 
                # Synchronize the main process with the job processes to
                # ensure proper cleanup.
                pool.close()
                pool.join()
                print "Processed " + gdb
                print datetime.datetime.now() - proTime
    ##        numProc = len(gdbs)
    ##        pool = multiprocessing.Pool(processes=numProc)
    ##        pool.map(meanArea, gdbs) 
    ##        # Synchronize the main process with the job processes to
    ##        # ensure proper cleanup.
    ##        pool.close()
    ##        pool.join()
    ##        print "The scipt executed in: "
    ##        print datetime.datetime.now() - proTime
    print "The scipt executed in: "
    print datetime.datetime.now() - runTime

if __name__ == '__main__':
    main()

