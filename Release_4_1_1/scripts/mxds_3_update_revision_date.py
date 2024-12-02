#Jane Mills
#GPW

import arcpy, os


inFolder = r'\\Dataserver1\gpw\GPW4\Release_411\cartographic\mxd_CIESIN_411_website'

mxdList = [m for m in os.listdir(inFolder) if m[-4:] == ".mxd" and m[-8:] != "data.mxd"]
mxdList.sort()

for m in mxdList:
    print m
    mPath = os.path.join(inFolder,m)

    mxd = arcpy.mapping.MapDocument(mPath)

    title = arcpy.mapping.ListLayoutElements(mxd,"TEXT_ELEMENT", "DataSetTitle")[0]
    title.text = title.text.replace("v4.10","v4.11")

    copy = arcpy.mapping.ListLayoutElements(mxd,"TEXT_ELEMENT", "Copyright")[0]
    copy.text = copy.text.replace("2017","2018")

    desc = arcpy.mapping.ListLayoutElements(mxd,"TEXT_ELEMENT", "MapDescription")[0]
    desc.text = desc.text.replace("Revision 10","Revision 11")

    credit = arcpy.mapping.ListLayoutElements(mxd,"TEXT_ELEMENT", "MapCredit")[0]
    credit.text = credit.text.replace("September 2017","December 2018")

    footer = arcpy.mapping.ListLayoutElements(mxd,"TEXT_ELEMENT", "FooterText")[0]
    newText = footer.text.replace("Revision 10","Revision 11")
    newText = newText.replace("2017","2018")
    footer.text = newText

    mxd.save()

