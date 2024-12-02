#Jane Mills
#5/18/2017
#Add UCADMIN codes to gridding boundaries

# Import Libraries
import arcpy, os

tableFolder = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\pop_tables'
gridding = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\boundaries\gridding_boundaries_4_1_updated.gdb'

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
    admin = int(fc[-17])

    if admin > 0:
        gdb = os.path.join(tableFolder,iso+'.gdb')
        arcpy.env.workspace = gdb
        tableList = arcpy.ListTables("*lookup")
        if len(tableList)> 0:
            table = tableList[0]

            fieldList = ['UBID']
            for i in range(1,admin+1):
                field = arcpy.ListFields(table,"UCADMIN"+str(i))[0]
                fieldList.append(field.name)

            adminDict = {}
            with arcpy.da.SearchCursor(table,fieldList) as cursor:
                for row in cursor:
                    adminDict[row[0]] = row[1:]

            fieldList.append('CONTEXT')
            fieldList.append('WATER_CODE')
            with arcpy.da.UpdateCursor(fcPath,fieldList) as cursor:
                for row in cursor:
                    if row[0] in adminDict:
                        row[1:-2] = adminDict[row[0]]
                        cursor.updateRow(row)
                    elif row[-2] == 0 and row[-1] == 'L':
                        print "did not find ubid:", row[0]

            del adminDict

        else:
            print "did not find table"

print 'done'

