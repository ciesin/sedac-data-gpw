#Jane Mills
#5/18/2017
#Add NAME0 and UCADMIN0 to gridding boundaries

# Import Libraries
import arcpy, os

gridding = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\boundaries\gridding_boundaries_4_1.gdb'
table = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\centroids\ancillary.gdb\admin0_names_codes'

dataDict = {}
with arcpy.da.SearchCursor(table,['ISO','ISO_Numeric','Country']) as cursor:
    for row in cursor:
        dataDict[row[0]] = row[1:]

arcpy.env.workspace = gridding
fcList = arcpy.ListFeatureClasses()
fcList.sort()

fields = ['ISOALPHA','UCADMIN0','NAME0']

for fc in fcList:
    iso = fc[:3].upper()
    print iso

    data = dataDict[iso]
    admin0 = data[0]
    name0 = data[1]

    #Add to centroids
    with arcpy.da.UpdateCursor(fc,fields) as cursor:
        for row in cursor:
            row[0] = iso
            row[1] = admin0
            row[2] = name0
            cursor.updateRow(row)

print 'done'

