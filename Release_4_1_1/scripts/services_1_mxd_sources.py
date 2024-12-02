#Jane Mills
#GPW
#Change data source of service mxds

import arcpy, os


inFolder = r'F:\arcgisserver\serverdata\gpw'

folderList = [f for f in os.listdir(inFolder) if "rev11" in f]
folderList.sort()

for f in folderList[1:-2]:
    print(f)
    dataFolder = os.path.join(inFolder,f,'data')
    mxdPath = os.path.join(inFolder,f,'map-services',f.replace("-","_")+".mxd")

    mxd = arcpy.mapping.MapDocument(mxdPath)

    lyrs = arcpy.mapping.ListLayers(mxd,"*")

    for lyr in lyrs:
        dataName = lyr.name.replace("-","_")+"_30_sec.tif"
        lyr.replaceDataSource(dataFolder, "NONE", dataName, False)

    mxd.save()

