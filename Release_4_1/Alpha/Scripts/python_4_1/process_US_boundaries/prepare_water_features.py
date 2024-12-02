import arcpy, os

inGDB = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Preprocessing\Global\Water\working\usa\boundary_water_features.gdb'
arcpy.env.workspace = inGDB

fcList = arcpy.ListFeatureClasses()
fcList.sort()

fields = ['OBJECTID','Shape','UBID','Shape_Length','Shape_Area']

for fc in fcList:
    print fc

    fList = arcpy.ListFields(fc)

    for f in fList:
        if f.name in fields:
            pass
        else:
            arcpy.DeleteField_management(fc,f.name)
    
