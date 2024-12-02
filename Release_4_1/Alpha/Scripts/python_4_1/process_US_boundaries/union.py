import arcpy, os

bounds = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Preprocessing\Global\Water\working\usa\boundary_water_features.gdb'
glims = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Preprocessing\Global\Water\working\usa\glims.gdb'
hydros = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Preprocessing\Global\Water\working\usa\hydrography.gdb'

outGDB = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Preprocessing\Global\Water\working\usa\water_masks_union.gdb'
finalGDB = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Preprocessing\Global\Water\water_masks_usa.gdb'
template = os.path.join(outGDB,"template")

arcpy.env.workspace = bounds

fcList = arcpy.ListFeatureClasses()
fcList.sort()

for fc in fcList:
    print fc

    glim = os.path.join(glims,fc[:6]+"_glims")
    hydro = os.path.join(hydros,fc[:6]+"_hydrography")

    outUnion = os.path.join(outGDB,fc[:6]+"_union")
    arcpy.Union_analysis([fc,glim,hydro],outUnion,"NO_FID")

    outTemp = os.path.join(finalGDB,fc[:6]+"_water_mask")
    arcpy.Copy_management(template,outTemp,"FeatureClass")

    arcpy.Append_management(outUnion,outTemp,"NO_TEST")

    with arcpy.da.UpdateCursor(outTemp,['ISO','SWBDID']) as cursor:
        for row in cursor:
            row[0] = "USA"
            row[1] = " "
            cursor.updateRow(row)
    



