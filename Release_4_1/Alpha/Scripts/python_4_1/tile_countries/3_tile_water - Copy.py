import arcpy, os
intersectOutput = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\boundaries\working\bra.gdb\bra_water_intersect'
waterFolder = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\water_masks\tiles'

names = []
with arcpy.da.SearchCursor(intersectOutput,"tile") as cursor:
    for row in cursor:
        if not row[0] in names:
            names.append(row[0])

for n in names:
    outName = "bra_"+n+"_water_mask.shp"
    arcpy.FeatureClassToFeatureClass_conversion(intersectOutput,waterFolder,outName,"tile = '"+n+"'")

    arcpy.DeleteField_management(os.path.join(waterFolder,outName),'tile')
    arcpy.DeleteField_management(os.path.join(waterFolder,outName),'SHAPE_Leng')
    arcpy.DeleteField_management(os.path.join(waterFolder,outName),'SHAPE_Area')

print "done"

