# Kytt MacManus
# 9-14-15
# merge_rasters.py

import arcpy, os, datetime, multiprocessing, socket
     
        
def mergeGrids(rasterList):
    startTime = datetime.datetime.now()
    arcpy.CheckOutExtension("SPATIAL")
    templateRaster = rasterList[0]
    rootName = os.path.basename(os.path.dirname(templateRaster)).upper()   
    wildCard = os.path.basename(templateRaster).replace(rootName,"")
    iso = os.path.basename(templateRaster)[:3]
    outFolder = os.path.dirname(os.path.dirname(templateRaster))
    outRaster = r'F:\gpw\release_4_1\country_tifs\usa' + os.sep + iso + wildCard#[:-4]
    # define outExtent
    outExtent = r'\\Dataserver0\gpw\GPW4\Release_4_0\Prod\Gridding\global\ancillary\gpw4_extent.tif'
    arcpy.env.extent = outExtent
    if wildCard == "_MEAN_MASKED_ADMIN_AREA.tif":
        method = "MEAN"
    elif wildCard == "_PIXELID.tif":
        method = "FIRST"
    else:
        method = "SUM"
    try:
        arcpy.env.compression = "LZW"
        cellStats = arcpy.sa.CellStatistics(rasterList, method, "DATA")
        cellStats.save(outRaster)
        arcpy.CopyRaster_management(cellStats,outRaster[:-4]+'copy.tif')
        # success
        return "Rasterized " + outRaster + ": " + str(datetime.datetime.now()-startTime)
    except:
        return outRaster + " error: " + str(arcpy.GetMessages())

def main():
    scriptTime = datetime.datetime.now()
    # set workspaces and preprocess to attach paths
    host = socket.gethostname()
    if host == 'Devsedarc3':
        inWS = r'F:\gpw\release_4_1\country_tifs'
    elif host == 'Devsedarc4':
        inWS = r'D:\gpw\release_4_1\country_tifs'
    #r'\\Dataserver0\gpw\GPW4\Release_4_0\Prod\Gridding\country\pop_tables'
    arcpy.env.workspace = inWS
    rasterLists = []
    folders = arcpy.ListWorkspaces("usa*","Folder")
    for folder in folders:
        arcpy.env.workspace = folder
        subfolders = arcpy.ListWorkspaces("*","Folder")
        templateFolder = subfolders[0]
        rootName = os.path.basename(templateFolder).upper()   
        arcpy.env.workspace = templateFolder
        rasters = arcpy.ListRasters("*_E_ATOTPOPBT*2010*")
        # grab the wildcard
        for raster in rasters:
            
            inRasters = []
            wildCard = raster.replace(rootName,"")
            # cycle the subfolders and assemble the rasters
            for subfolder in subfolders:
                inRaster = subfolder + os.sep + os.path.basename(subfolder).upper() + wildCard
                inRasters.append(inRaster)
            rasterLists.append(inRasters)

    # multiprocess the data

    pool = multiprocessing.Pool(processes=1,maxtasksperchild=1)
    results = pool.map(mergeGrids, rasterLists)
    for result in results:
        print result
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()
    print "Script complete"
    print str(datetime.datetime.now()-scriptTime)

if __name__ == '__main__':
    main()
