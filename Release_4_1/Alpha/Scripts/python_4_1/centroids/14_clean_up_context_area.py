#Jane Mills
#3/31/2017
#Clean up context and area fields
#Add data context for units with zero pop
#Put in zeros for units with NULL context

# Import Libraries
import arcpy, os, csv

centroids = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\centroids\country_data.gdb'

arcpy.env.workspace = centroids
fcList = arcpy.ListFeatureClasses()
fcList.sort()

fields = ['GUBID','CONTEXT','CONTEXT_NM','WATER_CODE','TOTAL_A_KM','WATER_A_KM','LAND_A_KM','UN_2010_E']

for fc in fcList:
    if fc[:3] == 'usa':
        iso = fc[:6]
    else:
        iso = fc[:3]
    fcPath = os.path.join(centroids,fc)
    print iso

    with arcpy.da.UpdateCursor(fcPath,fields) as cursor:
        for row in cursor:
            if row[1] == 0:
                row[2] = "Not applicable"
            if row[3] is None:
                row[3] = 'L'
            if row[3] == 'IW':
                row[5] = row[4]
                row[6] = 0
            if row[1] is None:
                if row[7] == 0 and row[3] == 'L':
                    row[1] = 205
                    row[2] = 'Uninhabited'
                else:
                    row[1] = 0
            cursor.updateRow(row)

print 'done'

