import arcpy, os
rootFolder = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\boundaries'
waterFolder = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\water_masks'

isos = ['aus','bra','chn','ind','kaz']

for iso in isos:
    print iso
    inGDB = os.path.join(rootFolder,'working',iso+'.gdb')
    outGDB = os.path.join(rootFolder,'tiled_countries',iso+'.gdb')

    arcpy.env.workspace = inGDB
    inFC = arcpy.ListFeatureClasses()[0]

    dissolve = os.path.join(inGDB,iso+"_dissolve")
    arcpy.Dissolve_management(inFC, dissolve,"tile")

    water = os.path.join(waterFolder,iso+"_water_mask.shp")
    intersectOutput = os.path.join(inGDB,iso+"_water_mask_intersect")
    arcpy.Intersect_analysis([water,dissolve],intersectOutput,"NO_FID")

    names = []
    with arcpy.da.SearchCursor(intersectOutput,"tile") as cursor:
        for row in cursor:
            if not row[0] in names:
                names.append(row[0])

    for n in names:
        outName = iso+"_"+n+"_water_mask"
        arcpy.FeatureClassToFeatureClass_conversion(intersectOutput,outGDB,outName,"tile = '"+n+"'")

        arcpy.DeleteField_management(os.path.join(outGDB,outName),'tile')

print "done"

