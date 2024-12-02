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

# define function
def meanAdminArea(gdb):
    '''create mean admin unit area grids'''
    # set time counter
    startTime = datetime.datetime.now()
    arcpy.env.overwriteOutput = True
    # define paths
    gdbName = os.path.basename(gdb)
    iso = os.path.basename(gdb)[:-12]
    inFish = gdb + os.sep + iso + "_fishnet"
    sumTbl = gdb + os.sep + iso + "_mean_administrative_unit_area"
    validateView = iso + "_validate"
    validateExpression = '"SUM_AREAPOPPRODUCT" IS NULL'
    if int(arcpy.GetCount_management(arcpy.MakeTableView_management(sumTbl,validateView,validateExpression))[0])>0:    
        try:
            # change workspace to gdb
            arcpy.env.workspace = gdb
            # define input fishnet and check to see if it exists
            inFish = gdb + os.sep + iso + "_fishnet"
            # Check out Spatial Analyst License
            arcpy.CheckOutExtension("SPATIAL")
            arcpy.env.overwriteOutput=True
            # Define pixel id
            pixelID = "PIXELID"
                
            # define intersect file
            # check to see if the file is in the GDB, if it is assign it to a
            # variable otherwise kill the script
            # list files ending in fishnet_clipped_intersect
            intersect = gdb + os.sep + iso + "_fishnet_intersect"
            
            # Add "AREAPOPPRODUCT" field to derive weighting scheme
            areaPop = "AREAPOPPRODUCT"
##            arcpy.AddField_management(intersect,areaPop,"DOUBLE")
##            arcpy.AddField_management(inFish,"NUMINPUTS","DOUBLE")
            intLyr = iso + "_intlyr"
            arcpy.MakeFeatureLayer_management(intersect,intLyr)
            arcpy.CalculateField_management(intLyr,areaPop,"!ADMINAREAKM! * !E_ATOTPOPBT_2010!" , "PYTHON")
            # Calculate summary statistics to derive pixel values for input ADMINAREAKM and AREAPOPPRODUCT
            # define output file
            sumTbl = gdb + os.sep + iso + "_mean_administrative_unit_area"
            
            # define fields to sum
            sumFields = [["E_ATOTPOPBT_2010","SUM"],[areaPop,"SUM"]]
            
            arcpy.Statistics_analysis(intersect,sumTbl,sumFields,pixelID)
            arcpy.AddIndex_management(sumTbl,pixelID,pixelID + "_index","UNIQUE")
            # list fields to join from sumTable
            cntFields = arcpy.ListFields(sumTbl,"SUM*")
            
            joinFields = ['PIXELID','FREQUENCY']
            targFields = ['PIXELID','NUMINPUTS']
            # add fields to fishnet
            for cntField in cntFields:
                joinFields.append(cntField.name)
                newName = str(cntField.name).replace("SUM_","")
                targFields.append(newName)
##                arcpy.AddField_management(inFish,newName,"DOUBLE")
            # create dictionary of table values     
            joinDict = {}
            with arcpy.da.SearchCursor(sumTbl, joinFields) as rows:
                for row in rows:
                    joinval = row[0]
                    val1 = row[1]
                    val2 = row[2]
                    val3 = row[3]
                    joinDict[joinval]=[val1,val2,val3]
            del row, rows
            # create update cursor
            with arcpy.da.UpdateCursor(inFish, targFields) as recs:
                for rec in recs:
                    keyval = rec[0]
                    if joinDict.has_key(keyval):
                        rec[1] = joinDict[keyval][0]
                        rec[2] = joinDict[keyval][1]
                        rec[3] = joinDict[keyval][2]
                    else:
                        rec[1] = None
                        rec[2] = None
                        rec[3] = None
                    recs.updateRow(rec)
            del rec, recs
            gdb = r'F:\gpw\global\rasters' + os.sep + iso + ".gdb"
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
            outAreaPopGrid = gdb + os.path.sep + iso.upper() + "_AREAPOPPRODUCT" 
            arcpy.PolygonToRaster_conversion(inFish,"AREAPOPPRODUCT",outAreaPopGrid,'CELL_CENTER','#',cellSize)
##            outAdminPopGrid = gdb + os.path.sep + iso.upper() + "_E_ATOTPOPBT_2010_ADMIN" 
##            arcpy.PolygonToRaster_conversion(inFish,"E_ATOTPOPBT_2010",outAdminPopGrid,'CELL_CENTER','#',cellSize)
##            outInputs = gdb + os.path.sep + iso.upper() + "_NUMINPUTS" 
##            arcpy.PolygonToRaster_conversion(inFish,"NUMINPUTS",outInputs,'CELL_CENTER','#',cellSize)
    ##        meanUnits = gdb + os.path.sep + iso + "_MEAN_ADMIN_UNIT_AREA"
    ##        meanUnitArea = arcpy.sa.Divide(outAreaPopGrid,outAdminPopGrid)
    ##        meanUnitArea.save(meanUnits)    
            # success
            return "Reprocessed " + iso.upper() + ": " + str(datetime.datetime.now()-startTime)
        except:
            return iso.upper() + " error: " + str(arcpy.GetMessages())
    else:
        return 1


    
# define a main in order to test and troubleshoot functions
def main():
    scriptTime = datetime.datetime.now()
##    gdb = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\country\inputs\abw_fishnet.gdb'
##    print calculateEstimates(gdb)
##    print calculateSexProportions(gdb)
##    print joinSexData(gdb)
##    print calculateAdminAreas(gdb)
##    print joinEstimatesCalculateDensities(gdb)
##    print intersect(gdb)
##    print calculateIntersectCounts(gdb)
##    print gridAndSummarize(gdb)
##    print meanAdminArea(gdb)
    workspace = r'F:\gpw\global\fishnets'
    usaSpace = r'E:\gpw\v4processing\usa\fishnets'
    tiledSpace = r'E:\gpw\v4processing\tiled_countries\fishnets'
    workspaces = [r'Z:\GPW4\Beta\Gridding\country\fishnets_and_clipped_water']#usaSpace,tiledSpace
    # parse workspaces to make 1 master list
    gdb_list = []
    for ws in workspaces:
        arcpy.env.workspace = ws
        gdbs = arcpy.ListWorkspaces('*',"FILEGDB")
        gdbs.sort(reverse=False)
        gdb_temp = [os.path.join(ws, gdb) for gdb in gdbs]
        for gdbt in gdb_temp:
            gdb_list.append(gdbt)    
       
    print "processing"
    print len(gdb_list)
    # create multi-process pool and execute tool
    pool = multiprocessing.Pool(processes=30,maxtasksperchild=1)
    results = pool.map(meanAdminArea, gdb_list)
    print(results)
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()
                                       
                                       
    print "Script Complete in " + str(datetime.datetime.now()-scriptTime)
if __name__ == '__main__':
    main()
    












