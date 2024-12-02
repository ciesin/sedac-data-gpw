# Kytt MacManus
# 4-25-14

# import libraries
import os, arcpy, sys
import datetime
import multiprocessing

def meanArea(gdb):
    # Define pixel id
    pixelID = "PIXELID"
    # parse iso code
    iso = os.path.basename(gdb)[:-4]
    
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
    popList = arcpy.ListFields(intersect,"ATOTPOPBT")
    if len(popList) == 1:
        totPop1 = popList[0]
        totPop = totPop1.name
        print totPop
    else:
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
        areaPop = "AREAPOPPRODUCT"
        adminPop = "ATOTPOPBT_ADMIN"
        arcpy.AddField_management(intersect,areaPop,"DOUBLE")
        arcpy.AddField_management(intersect,adminPop,"DOUBLE")
        # also add it to inFish
        arcpy.AddField_management(inFish,"SUM_" + areaPop,"DOUBLE")     
        arcpy.AddField_management(inFish,"SUM_" + adminPop,"DOUBLE")
        arcpy.AddField_management(inFish,"NUMINPUTS","DOUBLE")
        print "Added " + areaPop + " and " + adminPop
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
        arcpy.GetMessages()

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
        arcpy.GetMessages()

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
    wsRoot = gdb.replace(os.path.basename(gdb),"")
    outputRoot = wsRoot.replace("states","rasters")
    outGDB = iso.lower() + "_grids"
    outputGDB = outputRoot + outGDB + ".gdb"
    try:
        gridTime = datetime.datetime.now()
        outAreaPopGrid = outputGDB + os.path.sep + iso.upper() + "_AREAPOPPRODUCT" 
        arcpy.PolygonToRaster_conversion(inFish,"SUM_AREAPOPPRODUCT",outAreaPopGrid,'CELL_CENTER','#',cellSize)
        print "Created " + outAreaPopGrid
        print datetime.datetime.now() - gridTime
    except:
        print arcpy.GetMessages()
    try:
        gridTime = datetime.datetime.now()
        outAdminPopGrid = outputGDB + os.path.sep + iso.upper() + "_ATOTPOPBT_ADMIN" 
        arcpy.PolygonToRaster_conversion(inFish,"SUM_ATOTPOPBT_ADMIN",outAdminPopGrid,'CELL_CENTER','#',cellSize)
        print "Created " + outAdminPopGrid
        print datetime.datetime.now() - gridTime
    except:
        print arcpy.GetMessages()
    try:
        gridTime = datetime.datetime.now()
        outInputs = outputGDB + os.path.sep + iso.upper() + "_NUMINPUTS" 
        arcpy.PolygonToRaster_conversion(inFish,"NUMINPUTS",outInputs,'CELL_CENTER','#',cellSize)
        print "Created " + outInputs
        print datetime.datetime.now() - gridTime
    except:
        print arcpy.GetMessages()
    # Create Country Level Mean Unit Grid
    try:      
        gridTime = datetime.datetime.now()
        meanUnits = outputGDB + os.path.sep + iso.upper() + "_MEAN_ADMIN_UNIT_AREA"
        meanUnitArea = arcpy.sa.Divide(outAreaPopGrid,outAdminPopGrid)
        meanUnitArea.save(meanUnits)
        print "Created " + meanUnits
        print datetime.datetime.now() - gridTime
    except:
        print arcpy.GetMessages()
    
def main():
    # Check out Spatial Analyst License
    arcpy.CheckOutExtension("SPATIAL")
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
####            meanArea(gdb)
    pool = multiprocessing.Pool(processes=12,maxtasksperchild=1)
    pool.map(meanArea, gdbs) 
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()

##    for gdb in gdbs:
##        print gdb
##        # define output workspace
##        meanArea(gdb)            
            
    print datetime.datetime.now() - startTime
if __name__ == '__main__':
    main()


        
        
