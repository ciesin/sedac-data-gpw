# -------------------------------------------------------------------------------
#Jane Mills
#1/18/2019
#recreate fishnets
# -------------------------------------------------------------------------------


import arcpy, os
arcpy.env.overwriteOutput = True

root = r'F:\gpwv411\processed_fishnets'
outFolder = os.path.join(root,'output_fishnets')
validGDB = os.path.join(root,'validation.gdb')
arcpy.env.scratchWorkspace = outFolder
natid = r'\\Dataserver1\gpw\GPW4\Release_411\data\boundaries\global_boundaries_admin0.gdb\national_identifier_polygon_30_sec'

gdbList = [os.path.join(outFolder,g) for g in os.listdir(outFolder)]
gdbList.sort()
print("Let's get going: {}".format(len(gdbList)))

#Build dict of null pixels (within natid)
nullPixels = {}
for gdb in gdbList:
    countryName = os.path.basename(gdb)[:-4]
    print(countryName)
    inFish = os.path.join(gdb,countryName+"_fishnet")
    
    arcpy.MakeFeatureLayer_management(inFish,"fishnet","AREAKM IS NULL")
    count = int(arcpy.GetCount_management("fishnet")[0])
    
    if count > 0:
        arcpy.SelectLayerByLocation_management("fishnet","HAVE_THEIR_CENTER_IN",natid)
        count1 = int(arcpy.GetCount_management("fishnet")[0])
        
        if count1 > 0:
            with arcpy.da.SearchCursor("fishnet","PIXELID") as cursor:
                for row in cursor:
                    if row[0] in nullPixels:
                        nullPixels[row[0]] += 1
                    else:
                        nullPixels[row[0]] = 1


print(len(nullPixels))

#Get rid of pixels that aren't null in other countries
for gdb in gdbList:
    countryName = os.path.basename(gdb)[:-4]
    print(countryName)
    inFish = os.path.join(gdb,countryName+"_fishnet")
    with arcpy.da.SearchCursor(inFish,"PIXELID","AREAKM IS NOT NULL") as cursor:
        for row in cursor:
            if row[0] in nullPixels:
                nullPixels[row[0]] = 0

coastalNulls = {}
for key in nullPixels:
    if nullPixels[key] != 0:
        coastalNulls[key] = nullPixels[key]

print(len(coastalNulls))


#Everything worked! Any nulls in one fishnet are not nulls in other fishnets
#Or they don't have their center in the national identifier - they must have slivers 
#touching that are lost in the intersection


#Delete null pixels
for gdb in gdbList:
    countryName = os.path.basename(gdb)[:-4]
    inFish = os.path.join(gdb,countryName+"_fishnet")
    fList = [f.name for f in arcpy.ListFields(inFish) if not f.required and not f.name in ['Id','gridcode','PIXELID','PIXELAREA']]
    count = 0
    with arcpy.da.UpdateCursor(inFish,fList,"AREAKM IS NULL") as cursor:
        for row in cursor:
            if list(row).count(None) == len(row):
                cursor.deleteRow()
            else:
                count += 1
    if count > 0:
        print("{}: {} left".format(countryName,count))
    else:
        print(countryName)




