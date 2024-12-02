#Jane Mills
#3/23/2017
#Add area to centroids

# Import Libraries
import arcpy, os

centroids = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\centroids\country_data.gdb'
processFolder = r'D:\gpw\release_4_1\process'

arcpy.env.workspace = processFolder
gdbList = arcpy.ListWorkspaces("*","FILEGDB")

arcpy.env.workspace = centroids
cenList = arcpy.ListFeatureClasses()
cenList.sort()

for cen in cenList:
    if cen[:3] == 'usa':
        iso = cen[:5]
        gdbs = filter(lambda x: os.path.basename(x)[:5] == iso, gdbList)
    else:
        iso = cen[:3]
        gdbs = filter(lambda x: os.path.basename(x)[:3] == iso, gdbList)
    cenPath = os.path.join(centroids,cen)
    print iso
    areaDict = {}
    densDict = {}

    if len(gdbs) > 0:
        for gdb in gdbs:
            arcpy.env.workspace = gdb
            fcList = arcpy.ListFeatureClasses("*gridding")
            if len(fcList) == 1:
                gridFC = fcList[0]
                with arcpy.da.SearchCursor(gridFC,['UBID','AREAKM','WATERAREAKM','MASKEDAREAKM']) as cursor:
                    for row in cursor:
                        areaDict[row[0]] = row[1:]

            else:
                print "no feature classes found"

            tableList = arcpy.ListTables("*estimates")
            if len(tableList) == 1:
                table = tableList[0]
                with arcpy.da.SearchCursor(table,['UBID','UNE_ATOTPOPBT_2000_DSM','UNE_ATOTPOPBT_2005_DSM','UNE_ATOTPOPBT_2010_DSM','UNE_ATOTPOPBT_2015_DSM','UNE_ATOTPOPBT_2020_DSM']) as cursor:
                    for row in cursor:
                        densDict[row[0]] = row[1:]

            else:
                print "no tables found"

        with arcpy.da.UpdateCursor(cenPath,['UBID','TOTAL_A_KM','WATER_A_KM','LAND_A_KM','UN_2000_DS','UN_2005_DS','UN_2010_DS','UN_2015_DS','UN_2020_DS','CONTEXT','WATER_CODE']) as cursor:
            for row in cursor:
                if row[0] in areaDict:
                    areas = areaDict[row[0]]
                    row[1] = areas[0]
                    row[2] = areas[1]
                    row[3] = areas[2]
                    if row[3] < 0:
                        print row[0], "has negative area:",row[3]
                if row[0] not in areaDict:
                    print row[0], "not in gridding boundaries"
                if row[0] in densDict:
                    dens = densDict[row[0]]
                    row[4] = dens[0]
                    row[5] = dens[1]
                    row[6] = dens[2]
                    row[7] = dens[3]
                    row[8] = dens[4]
                if row[0] not in densDict and row[10] == 'L' and row[9] == 0:
                    print row[0], "not in estimates tables"
                cursor.updateRow(row)

    else:
        print "no gridding gdb found"

    del areaDict
    del densDict

print 'done'


