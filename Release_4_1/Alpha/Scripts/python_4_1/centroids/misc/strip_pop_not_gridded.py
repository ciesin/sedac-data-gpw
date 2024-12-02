#Jane Mills
#3/23/2017

# Import Libraries
import arcpy, os

centroids = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\centroids\country_data_usa.gdb'

arcpy.env.workspace = centroids
boundList = arcpy.ListFeatureClasses()
boundList.sort()

for bound in boundList:
    iso = bound[:6]
    print iso

    with arcpy.da.UpdateCursor(bound,['CONTEXT','CONTEXT_NM'],"CONTEXT = 206") as cursor:
        for row in cursor:
            if row[0] == 206:
                row[0] = 0
                row[1] = None
                cursor.updateRow(row)

print 'done'
