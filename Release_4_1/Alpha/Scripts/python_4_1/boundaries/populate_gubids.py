#Jane Mills
#1/13/2017
#Calculate GUBID and spit out UBIDs with no boundary context or join value

import os, arcpy

boundGDB = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\from_sde\country_boundaries_hi_res_1_20.gdb'
codes = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\topology\global_boundaries.gdb\admin0_codes'

cDict = {}
with arcpy.da.SearchCursor(codes,['ISO','ISO_Numeric']) as cursor:
    for row in cursor:
        cDict[row[0]] = row[1]

arcpy.env.workspace = boundGDB

boundList = arcpy.ListFeatureClasses()
boundList.sort()

for boundary in boundList:
    iso = boundary[:3]
    isoNum = cDict[iso]
    print iso

    #calculate the GUBID as 1+ISO+ObjectID
    with arcpy.da.UpdateCursor(boundary,['GUBID','OBJECTID']) as cursor:
        for row in cursor:
            row[0] = int('1'+isoNum+str(row[1]))
            cursor.updateRow(row)
        print "calculated GUBID"

