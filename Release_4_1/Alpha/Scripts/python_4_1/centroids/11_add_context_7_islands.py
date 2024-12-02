#Jane Mills
#3/23/2017
#Add the data context to the 7 islands we added

# Import Libraries
import arcpy, os, csv

centroids = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\centroids\country_data.gdb'

arcpy.env.workspace = centroids
fcList = arcpy.ListFeatureClasses()
fcList.sort()

isoList = ['atf','bvt','hmd','iot','sgs','spr','umi']

for fc in fcList:
    iso = fc[:3]

    if iso in isoList:
        print iso
        #Add to centroids
        with arcpy.da.UpdateCursor(fc,['CONTEXT','CONTEXT_NM','WATER_CODE']) as cursor:
            for row in cursor:
                row[0] = 203
                row[1] = "Not enumerated or not reported in census"
                row[2] = "L"
                cursor.updateRow(row)

print 'done'
