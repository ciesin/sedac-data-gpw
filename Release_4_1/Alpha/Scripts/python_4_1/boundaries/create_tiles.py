import arcpy, os

iso = 'grl'

rootFolder = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\boundaries\tiled_countries'
outFolder = os.path.join(rootFolder,iso+".gdb")
inFC = os.path.join(rootFolder,iso+"_working.gdb",iso+"_admin3_boundaries_2010")

nameList = []

with arcpy.da.SearchCursor(inFC,"tile") as cursor:
    for row in cursor:
        if row[0] in nameList:
            pass
        else:
            nameList.append(row[0])

print "found all names"
nameList.sort()

for name in nameList:
    outName = iso+"_"+name
    arcpy.FeatureClassToFeatureClass_conversion(inFC,outFolder,outName,"tile = '"+name+"'")

    arcpy.DeleteField_management(os.path.join(outFolder,outName),["tile","NAME2"])
    print "exported:"+name

print "done"
