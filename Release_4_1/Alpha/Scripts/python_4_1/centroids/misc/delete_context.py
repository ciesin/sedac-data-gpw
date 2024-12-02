#Jane Mills
#3/23/2017
#Add the data context

# Import Libraries
import arcpy, os, csv

centroids = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\centroids\country_data.gdb'

arcpy.env.workspace = centroids
boundList = arcpy.ListFeatureClasses()
boundList.sort()

for bound in boundList:
    iso = bound[:3]
    print iso

    with arcpy.da.UpdateCursor(bound,['CONTEXT','CONTEXT_NM','WATER_CODE']) as cursor:
        for row in cursor:
            row[0] = None
            row[1] = None
            row[2] = None
            cursor.updateRow(row)

print 'done'
