import arcpy

root = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\centroids\country_data.gdb'

arcpy.env.workspace = root
fcList = arcpy.ListFeatureClasses()
fcList.sort()

for fc in fcList:
    print fc

    with arcpy.da.UpdateCursor(fc,['F_2010_E','M_2010_E']) as cursor:
        for row in cursor:
            males = row[0]
            females = row[1]
            row[0] = females
            row[1] = males
            cursor.updateRow(row)

print "done"

