#Jane Mills

import os, arcpy

inGDB = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Preprocessing\Country\USA\Ingest\Boundary\2_inland_boundaries.gdb'
boundGDB = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\boundaries\us_boundaries_hi_res.gdb'
template = os.path.join(boundGDB,'template')

arcpy.env.workspace = inGDB

boundList = arcpy.ListFeatureClasses()
boundList.sort()

for boundary in boundList:
    iso = boundary[:6]
    print iso

    outFC = os.path.join(boundGDB,iso+"_admin5_boundaries_2010")
    arcpy.CopyFeatures_management(template,outFC)

    arcpy.Append_management(boundary,outFC,schema_type="NO_TEST")
    print "appended"



