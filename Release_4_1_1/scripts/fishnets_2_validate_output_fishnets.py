# -------------------------------------------------------------------------------
#Jane Mills
#1/18/2019
#make sure fishnets have correct number of units
# -------------------------------------------------------------------------------
import arcpy, os, datetime

startTime = datetime.datetime.now()

root = r'F:\gpwv411\processed_fishnets'
origFish = os.path.join(root,'orig_fishnets')
outFolder = os.path.join(root,'output_fishnets')
gdbList = os.listdir(origFish)
gdbList.sort()
print("Let's get going: {}".format(len(gdbList)))

for gdb in gdbList:
    countryName = gdb[:-4]
    inFish = os.path.join(origFish,gdb,countryName+"_fishnet")
    outFish = os.path.join(outFolder,gdb,countryName+"_fishnet")
    
    if arcpy.Exists(outFish):
        inCount = 0
        outCount = 0
        
        with arcpy.da.SearchCursor(inFish,"PIXELID") as cursor:
            for row in cursor:
                inCount += 1
        
        with arcpy.da.SearchCursor(outFish,"PIXELID") as cursor:
            for row in cursor:
                outCount += 1
                
        if inCount != outCount:
            arcpy.Delete_management(outFish)
            print("Deleted: "+countryName)


print("Script Complete in {}".format(datetime.datetime.now()-startTime))
