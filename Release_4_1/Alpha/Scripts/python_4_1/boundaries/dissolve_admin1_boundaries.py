#Jane Mills
#3/23/2017
#Add areas to centroids

# Import Libraries
import arcpy, os

tableFolder = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\pop_tables'
gridding = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\boundaries\gridding_boundaries_4_1.gdb'
outGDB = r'D:\gpw\release_4_1\dissolved_admin1_boundaries\gpw_4_1_admin1.gdb'

arcpy.env.workspace = gridding
fcList = arcpy.ListFeatureClasses()
fcList.sort()

for fc in fcList:
    if fc[:3] == 'usa':
        iso = fc[:5]
    else:
        iso = fc[:3]
    print iso

    fcPath = os.path.join(gridding,fc)

    gdb = os.path.join(tableFolder,iso+'.gdb')
    arcpy.env.workspace = gdb
    tableList = arcpy.ListTables("*estimates")
    if len(tableList)> 0:
        table = tableList[0]

        fieldList = ['UBID']
        for field in fields:
            if field in [f.name for f in arcpy.ListFields(table)]:
                fieldList.append(field)

        if len(fieldList) > 1:
            dataDict = {}
    
            with arcpy.da.SearchCursor(table,fieldList) as cursor:
                for row in cursor:
                    dataDict[row[0]] = row[1:]

            fieldList.append('CONTEXT')
            fieldList.append('WATER_CODE')
            with arcpy.da.UpdateCursor(fcPath,fieldList) as cursor:
                for row in cursor:
                    if row[0] in dataDict:
                        row[1:-2] = dataDict[row[0]]
                        cursor.updateRow(row)
                    elif row[-2] == 0 and row[-1] == 'L':
                        print "did not find ubid:", row[0]

            del dataDict

print 'done'
