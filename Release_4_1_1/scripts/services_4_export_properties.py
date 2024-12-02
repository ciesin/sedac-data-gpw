#Jane Mills
#GPW
#Export text of service mxds

import arcpy, os, csv

inFolder = r'F:\arcgisserver\serverdata\gpw'
outCSV = r'\\Dataserver1\gpw\GPW4\Release_411\services\mxd_properties.csv'
headers = ['layer_name','layer_description','layer_credit','mxd_name','mxd_title',
           'mxd_summary','mxd_description','mxd_author','mxd_credit','mxd_tags']

with open(outCSV,"w") as csvOpen:
    csvMem = csv.writer(csvOpen)
    csvMem.writerow(headers)
    folderList = [f for f in os.listdir(inFolder) if "rev11" in f]
    folderList.sort()

    for f in folderList[:-1]:
        print(f)
        mxdPath = os.path.join(inFolder,f,'map-services',f.replace("-","_")+".mxd")
        mxd = arcpy.mapping.MapDocument(mxdPath)

        lyrs = arcpy.mapping.ListLayers(mxd,"*")

        for lyr in lyrs:
            csvMem.writerow([lyr.name,lyr.description,lyr.credits,
                             os.path.basename(mxdPath)[:-4],mxd.title,mxd.summary,
                             mxd.description, mxd.author,mxd.credits,mxd.tags])


