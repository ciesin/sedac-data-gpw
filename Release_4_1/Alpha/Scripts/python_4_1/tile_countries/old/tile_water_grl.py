import arcpy, os
inGDB = r'\\dataserver0\gpw\GPW4\Release_4_1\Alpha\Preprocessing\Global\Water\working\grl\tiles.gdb'
inFC = os.path.join(inGDB,'grl_water_mask_intersect_tiles')

tileList = []
with arcpy.da.SearchCursor(inFC,"tile") as cursor:
    for row in cursor:
        if row[0] not in tileList:
            tileList.append(row[0])

tileList.sort()

for tile in tileList:
    print tile
    outName = "grl_"+tile+"_water_mask"
    arcpy.FeatureClassToFeatureClass_conversion(inFC,inGDB,outName,"tile = '"+tile+"'")

    arcpy.DeleteField_management(os.path.join(inGDB,outName),"tile")

