#Jane Mills
#1/13/2017

import os, arcpy

boundGDB = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\boundaries\boundaries_used_for_gridding_4_1.gdb'

arcpy.env.workspace = boundGDB

boundList = arcpy.ListFeatureClasses()
boundList.sort()

for boundary in boundList[-14:]:
    print boundary

    #delete fields
    fList = arcpy.ListFields(boundary)
    fieldList = []
    for f in fList:
        if f.name == 'OBJECTID':
            pass
        elif f.name[:5] == 'SHAPE' or f.name[:5] == 'Shape':
            pass
        elif f.name == 'GUBID':
            pass
        else:
            fieldList.append(f.name)

    if len(fieldList) > 0:
        arcpy.DeleteField_management(boundary,fieldList)
        print "deleted fields"
