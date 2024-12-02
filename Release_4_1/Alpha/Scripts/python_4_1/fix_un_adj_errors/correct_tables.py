#Jane Mills
#11/29/17
#Fix UN pop in tables (devsedarc4 and network)

# Import Libraries
import arcpy, os, numpy

adjFactor = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\validation\adj_factors.gdb\un_wpp2015_adjustment_factors_11_29_17'
tables1 = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\tables\processed_pop_tables'
tables2 = r'D:\gpw\release_4_1\input_data\pop_tables'

#isoList = ['blr','bra','chl','cpv','cub','cyp','ggy','jey','lao','lca','mmr','phl','prk','sau','ssd','uga']
isoList = ['bra']

arcpy.env.workspace = tables1
gdbList1 = arcpy.ListWorkspaces()
arcpy.env.workspace = tables2
gdbList2 = arcpy.ListWorkspaces()
gdbList1.sort()
gdbList2.sort()

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


    inGDB1 = filter(lambda x: iso == os.path.basename(x)[:3], gdbList1)
    inGDB2 = filter(lambda x: iso == os.path.basename(x)[:3], gdbList2)
    
    for gdb in inGDB1+inGDB2:
        print os.path.basename(gdb)
        arcpy.env.workspace = gdb
        table1 = arcpy.ListTables("*estimates")[0]
        totals = numpy.array([0.0]*7)
        with arcpy.da.UpdateCursor(table1,fields,"E_ATOTPOPBT_2010 IS NOT NULL") as cursor:
            for row in cursor:
                row[7] = row[0]*(1+adj[0])
                row[8] = row[1]*(1+adj[1])
                row[9] = row[2]*(1+adj[2])
                row[10] = row[3]*(1+adj[3])
                row[11] = row[4]*(1+adj[4])
                row[12] = row[5]*(1+adj[5])
                row[13] = row[6]*(1+adj[6])
                totals += numpy.array(row[7:])
                cursor.updateRow(row)
        table2 = arcpy.ListTables("*total_pop_summary")

        if len(table2) == 1:
            print totals
            fields2 = ["SUM_"+f for f in fields[7:]]
            with arcpy.da.UpdateCursor(table2[0],fields2,"SUM_E_ATOTPOPBT_2010 IS NOT NULL") as cursor:
                for row in cursor:
                    row = list(totals)
                    cursor.updateRow(row)

print 'done'
