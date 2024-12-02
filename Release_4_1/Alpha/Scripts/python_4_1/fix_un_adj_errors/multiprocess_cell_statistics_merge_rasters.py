# multiprocess template
import os, datetime
import multiprocessing
import arcpy
scriptTime = datetime.datetime.now()
def process((wildcard,gridRasters)):
    processTime = datetime.datetime.now()
    arcpy.CheckOutExtension("SPATIAL")
    returnList = []
    try:
        # define outExtent
        outExtent = r'\\Dataserver0\gpw\GPW4\Release_4_0\Prod\Gridding\global\ancillary\gpw4_extent.tif'
        arcpy.env.extent = outExtent
        # define out loctions
        mosFolder = r'D:\gpw\release_4_1\merge'
        waterMask = r'D:\gpw\release_4_1\merge\gpw_v4_watermask.tif'
        variable = wildcard[:-4]
        outName = 'GPW' + variable + ".tif"
        outRaster = mosFolder + os.sep + outName
        cellStats = arcpy.sa.CellStatistics(gridRasters, "SUM", "DATA")
        arcpy.env.mask = cellStats
        snRaster = SetNull(Raster(waterMask)==0,Raster(cellStats))
        finalRaster = SetNull(Raster(snRaster)<0.0001,snRaster)
        finalRaster.save(outRaster)
        arcpy.BuildPyramidsandStatistics_management(outRaster)
        returnList.append("Processed "+ outName + " " + str(datetime.datetime.now()-processTime))
    except:
        returnList.append("Error while processing " + outName + " " + str(datetime.datetime.now()-processTime))
    return returnList

def main():
    workspace = r'D:\gpw\release_4_1\input_data\country_boundaries_hi_res.gdb'
    arcpy.env.workspace = workspace
    print "processing"
    # must create procList
    # each image service must add rasters from country_tifs and boundary_context_tifs
    countryTifsFolder = r'D:\gpw\release_4_1\country_tifs'
    # generate a list of countryTifFolders
    arcpy.env.workspace = countryTifsFolder
    countryList = arcpy.ListWorkspaces("*","FOLDER")
##    bcList = [os.path.join(bcTifsFolder,os.path.basename(iso)) for iso in countryList if arcpy.Exists(os.path.join(bcTifsFolder,os.path.basename(iso)))]
    procList = []
    wildcards =['_E_ATOTPOPBT_2015_CNTM.tif']#'_BOUNDARY_CONTEXT.tif']#'_PIXELAREA.tif']#'_WATERAREAKM.tif','_E_A065PLUSBT_2010_CNTM.tif','_E_A065PLUSMT_2010_CNTM.tif','_E_A065PLUSFT_2010_CNTM.tif',
##    wildcards = ['_E_A000_004BT_2010_CNTM.tif','_E_A000_004MT_2010_CNTM.tif','_E_A000_004FT_2010_CNTM.tif',
##                 '_E_ATOTPOPBT_2010_CNTM.tif','_AREAKMMASKED.tif']
    for wildcard in wildcards:
        addList = []
        for country in countryList:
            arcpy.env.workspace = country
            subFolders = arcpy.ListWorkspaces("*","FOLDER")
            if len(subFolders)==0:
                raster = country + os.sep + os.path.basename(country).upper() + wildcard 
                if not arcpy.Exists(raster):
                    print country + " is missing a raster for " + wildcard
                else:
                    addList.append(raster)
##                    bcRaster = raster.replace(countryTifsFolder,bcTifsFolder)
##                    if arcpy.Exists(bcRaster):
##                        addList.append(bcRaster)
            else:
                for subFolder in subFolders:
                    arcpy.env.workspace = subFolder
                    raster = subFolder + os.sep + os.path.basename(subFolder).upper() + wildcard 
                    if not arcpy.Exists(raster):
                        print subFolder + " is missing a raster for " + wildcard
                    else:
                        addList.append(raster)
##                        bcRaster = raster.replace(countryTifsFolder,bcTifsFolder)
##                        if arcpy.Exists(bcRaster):
##                            addList.append(bcRaster)
        procList.append((wildcard,addList))
                        
    pool = multiprocessing.Pool(processes=1,maxtasksperchild=1)
    results = pool.map(process, procList)
    for result in results:
        print result
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()
    print "Script Complete in " + str(datetime.datetime.now()-scriptTime)
 
if __name__ == '__main__':
    main()
