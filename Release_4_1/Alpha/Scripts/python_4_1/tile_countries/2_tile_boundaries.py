import arcpy, os
rootFolder = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\boundaries'

isos = ['aus','bra','chn','ind','kaz']

for iso in isos:
    print iso
    inGDB = os.path.join(rootFolder,'working',iso+'.gdb')

    arcpy.env.workspace = inGDB
    inFC = arcpy.ListFeatureClasses()[0]

    outGDB = os.path.join(rootFolder,'tiled_countries',iso+'.gdb')

    names = []
    with arcpy.da.SearchCursor(inFC,"tile") as cursor:
        for row in cursor:
            if not row[0] in names:
                names.append(row[0])

    for n in names:
        outName = iso+"_"+n
        arcpy.FeatureClassToFeatureClass_conversion(inFC,outGDB,outName,"tile = '"+n+"'")
        arcpy.DeleteField_management(os.path.join(outGDB,outName),"tile")

print "done"

