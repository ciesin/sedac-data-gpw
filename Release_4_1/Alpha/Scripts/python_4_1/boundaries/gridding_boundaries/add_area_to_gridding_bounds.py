#Jane Mills
#3/23/2017
#Add area to centroids

# Import Libraries
import arcpy, os

centroids = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\centroids\country_data.gdb'
gridding = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\boundaries\gridding_boundaries_4_1.gdb'

arcpy.env.workspace = gridding
fcList = arcpy.ListFeatureClasses()
fcList.sort()

arcpy.env.workspace = centroids
cenList = arcpy.ListFeatureClasses()
cenList.sort()

for fc in fcList:
    iso = fc[:-23]
    fcPath = os.path.join(gridding,fc)
    
    cenFC = filter(lambda x: x[:-10] == iso, cenList)
    cenPath = os.path.join(centroids,cenFC[0])
    
    print iso
    areaDict = {}

    with arcpy.da.SearchCursor(cenPath,['GUBID','TOTAL_A_KM','WATER_A_KM','LAND_A_KM']) as cursor:
        for row in cursor:
            areaDict[row[0]] = row[1:]

    arcpy.AlterField_management(fcPath,'TOTAL_A_KM','AREAKM','AREAKM')
    arcpy.AlterField_management(fcPath,'WATER_A_KM','WATERAREAKM','WATERAREAKM')
    arcpy.AlterField_management(fcPath,'LAND_A_KM','MASKEDAREAKM','MASKEDAREAKM')
    
    with arcpy.da.UpdateCursor(fcPath,['GUBID','AREAKM','WATERAREAKM','MASKEDAREAKM']) as cursor:
        for row in cursor:
            if row[0] in areaDict:
                areas = areaDict[row[0]]
                row[1] = areas[0]
                row[2] = areas[1]
                row[3] = areas[2]
            else:
                print row[0], "not in centroids"
            cursor.updateRow(row)

    del areaDict

print 'done'


