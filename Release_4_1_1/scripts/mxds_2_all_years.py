#Jane Mills
#GPW
#Create all years for pop count/density mxds

import arcpy, os


inFolder = r'\\Dataserver1\gpw\GPW4\Release_411\cartographic\mxd_CIESIN_411_website'

mxdList = [m for m in os.listdir(inFolder) if m[-4:] == ".mxd" and "2000" in m]
mxdList.sort()

years = [2005,2010,2015,2020]

dataFolder = r'\\Dataserver1\gpw\GPW4\Release_411\data\rasters_30sec'

for m in mxdList:
    print m
    mPath = os.path.join(inFolder,m)

    for year in years:
        print year
        outMXD = os.path.join(inFolder,m.replace('2000',str(year)))

        mxd = arcpy.mapping.MapDocument(mPath)

        popLyr = arcpy.mapping.ListLayers(mxd,"*population*.tif")[0]

        dataName = popLyr.name.replace("rev11_2000","rev11_"+str(year))
        popLyr.replaceDataSource(dataFolder, "NONE", dataName, False)
        popLyr.name = dataName

        title = arcpy.mapping.ListLayoutElements(mxd,"TEXT_ELEMENT", "DataSetTitle")[0]
        newTitle = title.text.replace("2000",str(year))
        title.text = newTitle

        mxd.saveACopy(outMXD)

