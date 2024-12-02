#Jane Mills
#GPW
#Export text of service mxds

import arcpy, os

inFolder = r'F:\arcgisserver\serverdata\gpw'
folderList = [f for f in os.listdir(inFolder) if "rev11" in f]
folderList.sort()

sldFolder = r'\\Dataserver1\gpw\GPW4\Release_411\services'
outSLDFolder = os.path.join(sldFolder,'slds')

for f in folderList[:-1]:
    if "count-" in f or "demographic" in f:
        inSLD = os.path.join(sldFolder,'sld_count.txt')
    elif "density" in f:
        inSLD = os.path.join(sldFolder,'sld_density.txt')
    elif "identifier" in f:
        inSLD = os.path.join(sldFolder,'sld_natid.txt')
    elif "area" in f:
        inSLD = os.path.join(sldFolder,'sld_area.txt')
        
    mxdPath = os.path.join(inFolder,f,'map-services',f.replace("-","_")+".mxd")
    mxd = arcpy.mapping.MapDocument(mxdPath)

    lyrs = arcpy.mapping.ListLayers(mxd,"*")

    for lyr in lyrs:
        print(lyr)
        if "quality" in f and "watermask" in lyr.name:
            inSLD = os.path.join(sldFolder,'sld_watermask.txt')
        if "quality" in f and "mean" in lyr.name:
            inSLD = os.path.join(sldFolder,'sld_maua.txt')
        if "quality" in f and "context" in lyr.name:
            inSLD = os.path.join(sldFolder,'sld_context.txt')

        outSLD = os.path.join(outSLDFolder,lyr.name+'.txt')
        openSLD = open(inSLD,'r')
        sldContents = openSLD.read()
        openSLD.close()

        newTitle = lyr.description
        newTitle = newTitle[4:newTitle.find(' map layer')]
        newTitle = newTitle.replace("_"," ")
        #print(newTitle)

        sldContents = sldContents.replace("gpw-v4-layername",lyr.name)
        sldContents = sldContents.replace("gpw-v4-stylename",lyr.name+":default")
        sldContents = sldContents.replace("gpw-v4-title",newTitle)
        sldContents = sldContents.replace("gpw-v4-abstract",lyr.description.replace("_"," "))

        openSLD = open(outSLD,'w')
        openSLD.write(sldContents)
        openSLD.close()


