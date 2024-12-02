#Jane Mills
#1/13/2017
#Calculate GUBID and spit out UBIDs with no boundary context or join value

import os, arcpy

isos = ['can','rus']

for iso in isos:

    bounds = os.path.join(r"F:\GPW\fishnets\country_boundaries_admin0\tiles",iso)
    codes = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\topology\global_boundaries.gdb\admin0_codes'

    cDict = {}
    with arcpy.da.SearchCursor(codes,['ISO','ISO_Numeric']) as cursor:
        for row in cursor:
            cDict[row[0]] = row[1]

    arcpy.env.workspace = bounds

    boundList = arcpy.ListFeatureClasses()
    boundList.sort()

    for boundary in boundList:
        isoNum = int(cDict[iso])
        print iso

        arcpy.AddField_management(boundary,"ID_0","LONG")
        arcpy.CalculateField_management(boundary,"ID_0",isoNum)

        
