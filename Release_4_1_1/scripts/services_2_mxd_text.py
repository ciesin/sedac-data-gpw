#Jane Mills
#GPW
#Change text of service mxds

import arcpy, os

inFolder = r'F:\arcgisserver\serverdata\gpw'

folderList = [f for f in os.listdir(inFolder) if "rev11" in f]
folderList.sort()

for f in folderList[1:-2]:
    print(f)
    mxdPath = os.path.join(inFolder,f,'map-services',f.replace("-","_")+".mxd")
    mxd = arcpy.mapping.MapDocument(mxdPath)

    if "demographic" in f:
        newDOI = "https://doi.org/10.7927/H46M34XX."
    elif "quality" in f:
        newDOI = "https://doi.org/10.7927/H42Z13KG."
    elif "land-water" in f:
        newDOI = "https://doi.org/10.7927/H4Z60M4Z."
    elif "national" in f:
        newDOI = "https://doi.org/10.7927/H4TD9VDP."
    elif "count-adjusted" in f:
        newDOI = "https://doi.org/10.7927/H4PN93PB."
    elif "count-rev" in f:
        newDOI = "https://doi.org/10.7927/H4JW8BX5."
    elif "density-adjusted" in f:
        newDOI = "https://doi.org/10.7927/H4F47M65."
    elif "density-rev" in f:
        newDOI = "https://doi.org/10.7927/H49C6VHW."

    lyrs = arcpy.mapping.ListLayers(mxd,"*")

    for lyr in lyrs:
        lyr.credits = 'NASA SEDAC'
        newText = lyr.description
        newText = newText.replace("v4.10","v4.11")
        newText = newText.replace("Revision 10","Revision 11")
        newText = newText.replace("  "," ")
        doiIndex = newText.find("https")
        newText = newText[:doiIndex] + newDOI
        lyr.description = newText

    mxd.title = mxd.title.replace("Revision 10","Revision 11")
    mxd.description = mxd.description.replace("Revision 10","Revision 11")
    mxd.tags = mxd.tags.replace("rev10","rev11")
    
    mxd.save()

