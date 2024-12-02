import arcpy, os

inGDB = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Preprocessing\Country\USA\Ingest\Boundary\1_tiger_projected.gdb'
arcpy.env.workspace = inGDB

outGDB1 = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Preprocessing\Country\USA\Ingest\Boundary\2_inland_boundaries.gdb'
outGDB2 = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Preprocessing\Country\USA\Ingest\Boundary\3_dissolved_coastlines.gdb'

outGDB3 = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Preprocessing\Global\Water\working\usa\boundary_water_features.gdb'

fcList = arcpy.ListFeatureClasses()
fcList.sort()

for fc in fcList:
    print fc

    outFC1 = os.path.join(outGDB1, fc+"_inland")
    arcpy.FeatureClassToFeatureClass_conversion(fc,outGDB1,fc+"_inland","coastal_water = 0")

    outFC2 = os.path.join(outGDB2,fc+"_coastline")
    arcpy.Dissolve_management(outFC1, outFC2,"STATEFP10")

    arcpy.FeatureClassToFeatureClass_conversion(fc,outGDB3,fc+"_water_features","BOUNDARY_CONTEXT = 7 AND coastal_water = 0")



