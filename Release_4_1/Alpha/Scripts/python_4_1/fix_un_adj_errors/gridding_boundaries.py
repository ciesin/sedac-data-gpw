#Jane Mills
#11/29/17
#Fix UN pop in gridding boundaries

# Import Libraries
import arcpy, os, numpy

adjFactor = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\validation\adj_factors.gdb\un_wpp2015_adjustment_factors_11_29_17'
gridding = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\boundaries\gridding_boundaries_4_1.gdb'

arcpy.env.workspace = gridding
fcList = arcpy.ListFeatureClasses()
fcList.sort()

fields = ['E_ATOTPOPBT_1975','E_ATOTPOPBT_1990','E_ATOTPOPBT_2000','E_ATOTPOPBT_2005','E_ATOTPOPBT_2010','E_ATOTPOPBT_2015',
          'E_ATOTPOPBT_2020','UNE_ATOTPOPBT_1975','UNE_ATOTPOPBT_1990','UNE_ATOTPOPBT_2000','UNE_ATOTPOPBT_2005',
          'UNE_ATOTPOPBT_2010','UNE_ATOTPOPBT_2015','UNE_ATOTPOPBT_2020']

adjDict = {}
adjFields = ['GPW4_ISO','UNADJFAC_1975','UNADJFAC_1990','UNADJFAC_2000','UNADJFAC_2005','UNADJFAC_2010','UNADJFAC_2015','UNADJFAC_2020']
with arcpy.da.SearchCursor(adjFactor,adjFields) as cursor:
    for row in cursor:
        adjDict[row[0]] = row[1:]

isoList = ['blr','bra','chl','cpv','cub','cyp','ggy','jey','lao','lca','mmr','phl','prk','sau','ssd','uga']

for iso in isoList:
    print iso
    fcPath = os.path.join(gridding,filter(lambda x: iso == x[:3], fcList)[0])

    adj = adjDict[iso.upper()]
    totals = numpy.array([0.0]*7)
    with arcpy.da.UpdateCursor(fcPath,fields,"E_ATOTPOPBT_2010 IS NOT NULL") as cursor:
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

    for t in totals:
        print t

print 'done'
