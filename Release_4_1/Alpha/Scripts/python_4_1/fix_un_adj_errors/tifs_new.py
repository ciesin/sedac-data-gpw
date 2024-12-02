#Jane Mills
#11/30/17
#Move incorrect UN adjusted tifs to another location on devsedarc4

# Import Libraries
import arcpy, os
from arcpy.sa import *
arcpy.CheckOutExtension("Spatial")

adjFactor = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\validation\adj_factors.gdb\un_wpp2015_adjustment_factors_11_29_17'
root = r'D:\gpw\release_4_1\country_tifs'

isoList = ['blr','bra','chl','cpv','cub','cyp','ggy','jey','lao','lca','mmr','phl','prk','sau','ssd','uga']

adjDict = {}
adjFields = ['GPW4_ISO','UNADJFAC_1975','UNADJFAC_1990','UNADJFAC_2000','UNADJFAC_2005','UNADJFAC_2010','UNADJFAC_2015','UNADJFAC_2020']
with arcpy.da.SearchCursor(adjFactor,adjFields) as cursor:
    for row in cursor:
        adjDict[row[0]] = row[1:]

for iso in isoList:
    print iso
    adj = adjDict[iso.upper()]
    inFolder = os.path.join(root,iso)

    if iso == "bra":
        subFolders = os.listdir(inFolder)
        for sub in subFolders:
            print sub
            subPath = os.path.join(inFolder,sub)
            #List atotpopbt rasters
            arcpy.env.workspace = subPath
            rasterList = arcpy.ListRasters("*_E_ATOTPOPBT*")
            rasterList.sort()

            for i in range(len(rasterList)):
                r = rasterList[i]
                outR = r.replace("_E_ATOTPOPBT_","_UNE_ATOTPOPBT_")
                radj = 1+adj[i]
                outTimes = Times(r, radj)
                outTimes.save(os.path.join(subPath,outR))

            print "fixed rasters"

    else:
        #List atotpopbt rasters
        arcpy.env.workspace = inFolder
        rasterList = arcpy.ListRasters("*_E_ATOTPOPBT*")
        rasterList.sort()

        for i in range(len(rasterList)):
            r = rasterList[i]
            outR = r.replace("_E_ATOTPOPBT_","_UNE_ATOTPOPBT_")
            radj = 1+adj[i]
            outTimes = Times(r, radj)
            outTimes.save(os.path.join(inFolder,outR))

        print "fixed rasters"


print 'done'
