# -------------------------------------------------------------------------------
#Jane Mills
#1/18/2019
#recreate fishnets
# -------------------------------------------------------------------------------
import arcpy, os, multiprocessing, datetime
from arcpy.sa import *
arcpy.env.parallelProcessingFactor = "50%"
arcpy.env.overwriteOutput = True

startTime = datetime.datetime.now()

#####################################################################################################

def zstats(countryGDB):
    returnList = None
    
    # Set up all paths we'll need
    root = r'F:\gpwv411\processed_fishnets'
    tifs = os.path.join(root,'country_tifs')
    idTifs = os.path.join(root,'pixelid_tifs')
    outFolder = os.path.join(root,'output_fishnets')
    arcpy.env.scratchWorkspace = outFolder
    
    countryName = os.path.basename(countryGDB)[:-4]
    inFish = os.path.join(countryGDB,countryName+"_fishnet")
    
    outGDB = os.path.join(outFolder,countryName+".gdb")
    if not os.path.exists(outGDB):
        arcpy.CreateFileGDB_management(outFolder,countryName+".gdb")
    outFish = os.path.join(outGDB,countryName+"_fishnet")
    pixelTif = os.path.join(idTifs,countryName+"_PIXELID.tif")
    
    if not arcpy.Exists(outFish):
        countryTifs = [os.path.join(tifs,countryName,t) for t in os.listdir(os.path.join(tifs,countryName)) if t[-4:]=='.tif' and "PIXELAREA" not in t]
        memFish = 'in_memory' + os.sep + countryName
        arcpy.CopyFeatures_management(inFish,memFish)
        errorCount = 0
        zstatsErrors = 0
        if not os.path.exists(pixelTif):
            cs = arcpy.GetRasterProperties_management(countryTifs[0], "CELLSIZEX").getOutput(0)
            arcpy.PolygonToRaster_conversion(inFish, "PIXELID", pixelTif, "CELL_CENTER","",cs)
        for countryTif in countryTifs:
            try:
                outField = os.path.basename(countryTif)[len(countryName)+1:-4]
                memTable = 'in_memory' + os.sep + os.path.basename(countryTif)[:-4]
                ZonalStatisticsAsTable(pixelTif, "Value", countryTif, memTable, "DATA", "SUM")
                
                dataDict = {}
                with arcpy.da.SearchCursor(memTable,["Value","SUM","COUNT"]) as cursor:
                    for row in cursor:
                        dataDict[row[0]] = row[1]
                        if row[2] != 1:
                            zstatsErrors += 1
                
                arcpy.AddField_management(memFish,outField,"DOUBLE")
                with arcpy.da.UpdateCursor(memFish,["PIXELID",outField]) as cursor:
                    for row in cursor:
                        if row[0] in dataDict:
                            row[1] = dataDict[row[0]]
                            cursor.updateRow(row)
                        else:
                            zstatsErrors += 1
            except:
                errorCount += 1

        if errorCount == 0:
            arcpy.CopyFeatures_management(memFish,outFish)
            returnList = "Succeeded: {}: {} errors".format(countryName,str(zstatsErrors))
        else:
            returnList = "Failed: " + countryName
    else:
        returnList = "Already processed: " + countryName

    return returnList

#####################################################################################################

def main():    
    root = r'F:\gpwv411\processed_fishnets'
    outFolder = os.path.join(root,'output_fishnets')
    arcpy.env.scratchWorkspace = outFolder
    origFish = os.path.join(root,'orig_fishnets')
    gdbList = [os.path.join(origFish,g) for g in os.listdir(origFish)]
    gdbList.sort()
    print("Let's get going: {}".format(len(gdbList)))
    
    # Change the number of processes depending on the resolution
    pool = multiprocessing.Pool(processes=min([5,len(gdbList)]), maxtasksperchild=1)
    results = pool.map(zstats, gdbList)
    for result in results:
        print(result)

    pool.close()
    pool.join()
    
    endTime = datetime.datetime.now()
    
    print("Script Complete in {}".format(endTime-startTime))

#####################################################################################################

if __name__ == '__main__':
    main()

