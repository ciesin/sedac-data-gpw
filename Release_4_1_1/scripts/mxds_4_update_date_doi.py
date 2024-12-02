#Jane Mills
#GPW

import arcpy, os


inFolder = r'\\Dataserver1\gpw\GPW4\Release_411\cartographic\mxd_CIESIN_411_website'
outFolder = r'\\Dataserver1\gpw\GPW4\Release_411\cartographic\map_CIESIN_411_website'

mxdList = [m for m in os.listdir(inFolder) if m[-4:] == ".mxd" and m[-8:] != "data.mxd" and "ascii" not in m]
mxdList.sort()

for m in mxdList:
    print m
    mPath = os.path.join(inFolder,m)

    mxd = arcpy.mapping.MapDocument(mPath)

    #Just in case this comes out in 2019
    #copy = arcpy.mapping.ListLayoutElements(mxd,"TEXT_ELEMENT", "Copyright")[0]
    #copy.text = copy.text.replace("2018","2019")

    #credit = arcpy.mapping.ListLayoutElements(mxd,"TEXT_ELEMENT", "MapCredit")[0]
    #credit.text = credit.text.replace("December 2018","January 2019")

    if "center-point" in m:
        newDOI = "https://doi.org/10.7927/H4BC3WMT."
    elif "demographic" in m:
        newDOI = "https://doi.org/10.7927/H46M34XX."
    elif "quality" in m:
        newDOI = "https://doi.org/10.7927/H42Z13KG."
    elif "land-water" in m:
        newDOI = "https://doi.org/10.7927/H4Z60M4Z."
    elif "national" in m:
        newDOI = "https://doi.org/10.7927/H4TD9VDP."
    elif "count-adjusted" in m:
        newDOI = "https://doi.org/10.7927/H4PN93PB."
    elif "count-rev" in m:
        newDOI = "https://doi.org/10.7927/H4JW8BX5."
    elif "density-adjusted" in m:
        newDOI = "https://doi.org/10.7927/H4F47M65."
    elif "density-rev" in m:
        newDOI = "https://doi.org/10.7927/H49C6VHW."

    footer = arcpy.mapping.ListLayoutElements(mxd,"TEXT_ELEMENT", "FooterText")[0]
    #footer.text = footer.text.replace("2018","2019")
    doiIndex = footer.text.find("https")
    newText = footer.text[:doiIndex] + newDOI
    footer.text = newText

    mxd.save()

    #outPDF = os.path.join(outFolder,m[:-4]+".pdf")
    #arcpy.mapping.ExportToPDF(mxd, outPDF)
    

