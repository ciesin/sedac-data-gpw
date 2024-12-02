import arcpy, os

finals = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Preprocessing\Country\USA\Ingest\Boundary\2_inland_boundaries.gdb'
bounds40 = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\boundaries\us_boundaries_hi_res.gdb'
arcpy.env.workspace = finals

fcList = arcpy.ListFeatureClasses()
fcList.sort()

for fc in fcList:
    print fc[:6]

    old = os.path.join(bounds40,fc[:6])

    boundDict = {}
    with arcpy.da.SearchCursor(fc,"UBID","BOUNDARY_CONTEXT IS NULL") as cursor:
        for row in cursor:
            if row[0] in boundDict:
                print "duplicate UBID found: " + row[0]
            else:
                boundDict[row[0]] = 0

    oldDict = {}
    with arcpy.da.SearchCursor(old,"UBID","BOUNDARY_CONTEXT IS NULL") as cursor:
        for row in cursor:
            oldDict[row[0]] = 0
            if row[0] in boundDict:
                pass
            else:
                print "boundary not found in new feature class: " + row[0]

    for key in boundDict:
        if key in oldDict:
            pass
        else:
            print "boundary not found in old feature class: " + key





