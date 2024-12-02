#Jane Mills
#7/25/2018

import arcpy

gridding = r'\\Dataserver1\gpw\GPW4\Release_4_1\Alpha\Gridding\global\boundaries\gridding_boundaries_4_1.gdb'

arcpy.env.workspace = gridding
fcList = arcpy.ListFeatureClasses()
fcList.sort()

for fc in fcList:
    print fc
    count = 0
    with arcpy.da.UpdateCursor(fc,['CONTEXT','CONTEXT_NM'], "CONTEXT = 0") as cursor:
        for row in cursor:
            if row[1] is None:
                row[1] = 'Not applicable'
                cursor.updateRow(row)
            else:
                count += 1

    if count > 0:
        print "found {} rows with zero context but a code filled in".format(count)

print 'done'
