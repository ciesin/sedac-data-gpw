#Jane Mills
#5/18/2017
#Add UCADMIN codes to gridding boundaries

# Import Libraries
import arcpy

gridding = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\boundaries\gridding_boundaries_4_1.gdb'

fields = ['UBID','UCADMIN1','UCADMIN2','UCADMIN3','UCADMIN4','UCADMIN5']

arcpy.env.workspace = gridding
fcList = arcpy.ListFeatureClasses("usa*")
fcList.sort()

for fc in fcList:
    print fc[:5]

    with arcpy.da.UpdateCursor(fc,fields) as cursor:
        for row in cursor:
            row[1] = row[0][3:5]
            row[2] = row[0][5:8]
            row[3] = row[0][8:14]
            row[4] = row[0][14]
            row[5] = row[0][14:]
            cursor.updateRow(row)

pri = 'pri_admin4_boundaries_2010'
print 'pri'
with arcpy.da.UpdateCursor(pri,fields) as cursor:
    for row in cursor:
        row[1] = row[0][5:8]
        row[2] = row[0][8:14]
        row[3] = row[0][14]
        row[4] = row[0][14:]
        cursor.updateRow(row)

print 'done'

