#Jane Mills
#11/29/17
#Fix UN pop in processing tables and fishnets

# Import Libraries
import arcpy, os, numpy

adjFactor = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\validation\adj_factors.gdb\un_wpp2015_adjustment_factors_11_29_17'
inFolder = r'D:\gpw\release_4_1\process'

isoList = ['blr','bra','chl','cpv','cub','cyp','ggy','jey','lao','lca','mmr','phl','prk','sau','ssd','uga']

arcpy.env.workspace = inFolder
gdbList = arcpy.ListWorkspaces()
gdbList.sort()

fields = ['E_ATOTPOPBT_1975','E_ATOTPOPBT_1990','E_ATOTPOPBT_2000','E_ATOTPOPBT_2005','E_ATOTPOPBT_2010','E_ATOTPOPBT_2015',
          'E_ATOTPOPBT_2020','UNE_ATOTPOPBT_1975','UNE_ATOTPOPBT_1990','UNE_ATOTPOPBT_2000','UNE_ATOTPOPBT_2005',
          'UNE_ATOTPOPBT_2010','UNE_ATOTPOPBT_2015','UNE_ATOTPOPBT_2020']

adjDict = {}
adjFields = ['GPW4_ISO','UNADJFAC_1975','UNADJFAC_1990','UNADJFAC_2000','UNADJFAC_2005','UNADJFAC_2010','UNADJFAC_2015','UNADJFAC_2020']
with arcpy.da.SearchCursor(adjFactor,adjFields) as cursor:
    for row in cursor:
        adjDict[row[0]] = row[1:]

for iso in isoList:
    print iso
    adj = adjDict[iso.upper()]

    inGDB = filter(lambda x: iso == os.path.basename(x)[:3], gdbList)

    totals = numpy.array([0.0]*7)
    for gdb in inGDB:
        print os.path.basename(gdb)
        arcpy.env.workspace = gdb
        estTable = arcpy.ListTables("*estimates")[0]
        intTable = arcpy.ListTables("*estimates_table")
        fish = arcpy.ListFeatureClasses("*processed")

        with arcpy.da.UpdateCursor(estTable,fields,"E_ATOTPOPBT_2010 IS NOT NULL") as cursor:
            for row in cursor:
                row[7] = row[0]*(1+adj[0])
                row[8] = row[1]*(1+adj[1])
                row[9] = row[2]*(1+adj[2])
                row[10] = row[3]*(1+adj[3])
                row[11] = row[4]*(1+adj[4])
                row[12] = row[5]*(1+adj[5])
                row[13] = row[6]*(1+adj[6])
                cursor.updateRow(row)

        print "fixed estimates"

        fields1 = [f+"_CNTM" for f in fields]
        for table in intTable+fish:
            with arcpy.da.UpdateCursor(table,fields1,"E_ATOTPOPBT_2010_CNTM IS NOT NULL") as cursor:
                for row in cursor:
                    row[7] = row[0]*(1+adj[0])
                    row[8] = row[1]*(1+adj[1])
                    row[9] = row[2]*(1+adj[2])
                    row[10] = row[3]*(1+adj[3])
                    row[11] = row[4]*(1+adj[4])
                    row[12] = row[5]*(1+adj[5])
                    row[13] = row[6]*(1+adj[6])
                    cursor.updateRow(row)
        print "fixed fishnet"

        with arcpy.da.SearchCursor(fish[0],fields1,"E_ATOTPOPBT_2010_CNTM IS NOT NULL") as cursor:
            for row in cursor:
                totals += numpy.array(row[7:])

    print totals

print 'done'
