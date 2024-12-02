import arcpy, os

def create_tiles(iso):
    rootFolder = r'F:\GPW\fishnets\country_boundaries_admin0\tiles'
    outFolder = os.path.join(rootFolder,iso)
    inFC = os.path.join(rootFolder,iso+"_working.gdb",iso+"_fish")

    nameList = []

    with arcpy.da.SearchCursor(inFC,"NAME") as cursor:
        for row in cursor:
            nameList.append(row[0])

    for name in nameList:
        outName = iso+"_"+name+".shp"
        arcpy.FeatureClassToFeatureClass_conversion(inFC,outFolder,outName,"NAME = '"+name+"'")




create_tiles('rus')
print "done with russia"

create_tiles('can')
print "done with canada"
