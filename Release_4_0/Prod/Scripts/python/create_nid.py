# this script must be run on a computer with >100GB RAM
# completes in ~45 minutes
# we could add any types of additional criteria for classifying a raster from GPW


import arcpy, os, gdal, datetime, multiprocessing
import numpy as np
    
def readFishnets(gdb):
    ## read through the fishnets by pixelid and 
    ## create maxAreaDict
    fishnetDict={}
    iso = os.path.basename(gdb)[:3].upper()
##    print iso
    arcpy.env.workspace = gdb
    fishnet = arcpy.ListFeatureClasses("*processed")[0]
    with arcpy.da.SearchCursor(fishnet,["PIXELID","AREAKMMASKED"]) as scursor:
        for r in scursor:
            pixelid = r[0]
            area = r[1]
            fishnetDict[pixelid]=(iso,area)
    return fishnetDict



def main():
    scriptStart = datetime.datetime.now()
    # define and read country code table into a dictionary
    # where key = ISOCODE and value = UCADMIN0
    processStart = datetime.datetime.now()
    codeTable = r'\\Dataserver0\gpw\GPW4\Release_4_0\Prod\ancillary.gdb\gpw4_country_codes'
    codeDict = {}
    with arcpy.da.SearchCursor(codeTable,["ISO","UCADMIN0"]) as cursor:
        for row in cursor:
            iso = row[0].upper()
            code = row[1]
            codeDict[iso]=code
    print "Read UCADMIN Code Lookup "+ str(datetime.datetime.now()-processStart)
    
    # set workspace
    arcpy.env.workspace = r'D:/gpw/fishnets'
    gdbs = arcpy.ListWorkspaces("*","FileGDB")
##    gdbs2 = arcpy.ListWorkspaces("prt*","FileGDB")
##    gdbs = gdbs + gdbs2
    folders = arcpy.ListWorkspaces("*","Folder")
    for folder in folders:
        arcpy.env.workspace = folder + os.sep + 'tiles'
        gdbs2 = arcpy.ListWorkspaces("*","FileGDB")
        gdbs = gdbs + gdbs2

    processStart = datetime.datetime.now()
##    for gdb in gdbs:
##        fishnetDict = readFishnets(gdb) 
    # multiprocess the data
    pool = multiprocessing.Pool(processes=20,maxtasksperchild=1)
    fishnetDicts = pool.map(readFishnets, gdbs) 
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()
    print "Read fishnetDict Lookups " + str(datetime.datetime.now()-processStart)

    
    ## assign to a dictionary the country codes
    ## which are valid for a pixelid given the condition that the AREAKMMASKED with the largest
    ## value decides which country gets the assignment
    processStart = datetime.datetime.now()
    maxAreaDict = {}
    for fishnetDict in fishnetDicts:
        for pixelid, valueTuple in fishnetDict.iteritems():
            iso = valueTuple[0]
            area = valueTuple[1]   
            if not pixelid in maxAreaDict:
                maxAreaDict[pixelid]=(iso,area)
            else:
                # check to see if the area being considered
                # is larger than the assigned area
                storedArea = maxAreaDict[pixelid][1]
                if storedArea >= area:
                    continue
                else:
                    maxAreaDict[pixelid]=(iso,area)
        del fishnetDict
    print "Calculated PIXELID Lookup " + str(datetime.datetime.now()-processStart)
                               
    # Now that the classification of ISO Codes to PIXELIDs has occurred
    # We can read the grid of PIXELIDs and replace them is UCADMIN0 values
    # Create driver to produce GeoTiffs
    processStart = datetime.datetime.now()
    inIDS = r'D:\gpw\ancillary\gpw4_ids.tif'
    newFile = r'D:\gpw\ancillary\gpw4_nid.tif'
    outNID = r'D:\gpw\rasters\merge\gl.gdb\GL_NATIONAL_IDENTIFIER_GRID'
    driver = gdal.GetDriverByName("GTiff")
    # Open Extent File
    inputExtentOpen = gdal.Open(inIDS)
    # Set number of raster bands 
    nbands = inputExtentOpen.RasterCount
    # Set number of columns and rows for -180, -90, 90, 180 --Full Global Extent
    ncols = inputExtentOpen.RasterXSize
    nrows = inputExtentOpen.RasterYSize
    # Determine appropriate GDAL Data Type and Assign to Variable
    if ncols * nrows < 256:    
        # Set GDAL data type
        gdal_datatype = gdal.GDT_Byte
    elif ncols * nrows < 65536 and ncols * nrows > 255:
        gdal_datatype = gdal.GDT_UInt16
    elif ncols * nrows <  4294967296 and ncols * nrows > 65535:
        gdal_datatype = gdal.GDT_UInt32
    # Get input GeoTransform Information
    inputExtentGeoTransform = inputExtentOpen.GetGeoTransform()
    # Set lower left corner
    xllcorner = inputExtentGeoTransform[0]
    # Set upper left corner
    yulcorner = inputExtentGeoTransform[3]
    # Set cell size 
    cellsize = inputExtentGeoTransform[1]
    # convert the raster to an array
    ##print "Reading"
    inputArray = inputExtentOpen.ReadAsArray()
    # grab the length and noDataValue
    noDataValue = inputArray[0][0]
    numPixels = inputArray.size
    pixelidFlat = inputArray.reshape(numPixels)
    outputArrayFlat = []
    for pid in pixelidFlat.flat:
        if pid == noDataValue:
            outputArrayFlat.append(pid)
        else:
            # look up the value
            iso = maxAreaDict[pid][0]
            ucCode = codeDict[iso]
            outputArrayFlat.append(ucCode)
    # now reshape the array
    outputArray = np.array(outputArrayFlat).reshape(nrows,ncols)
    del maxAreaDict
    print "Completed classification " + str(datetime.datetime.now()-processStart)
    processStart = datetime.datetime.now()
    # Create new file
    newRaster = driver.Create(newFile,ncols,nrows,nbands,gdal_datatype)
    # Define geographic extent of new file
    newRaster.SetGeoTransform([xllcorner,cellsize,0,yulcorner,0,-cellsize])
    # Write sequential integer values to raster file
    newRaster.GetRasterBand(1).WriteArray(outputArray)
    # Clear locks
    newRaster = None
    # Use Arcpy to define projection
    try:
        WGS84 = arcpy.SpatialReference(4326)
        arcpy.DefineProjection_management(newFile, WGS84)
        arcpy.BuildRasterAttributeTable_management(newFile)
        arcpy.CheckOutExtension('Spatial')
        extract = arcpy.sa.ExtractByAttributes(newFile,"Value>0")
        extract.save(outNID)
        arcpy.BuildPyramids_management(outNID)
    except:
        print arcpy.GetMessages()   
    print "Created " + newFile + " " + str(datetime.datetime.now()-processStart)
    print "Completed script " + str(datetime.datetime.now()-scriptStart)

if __name__ == '__main__':
    main()
