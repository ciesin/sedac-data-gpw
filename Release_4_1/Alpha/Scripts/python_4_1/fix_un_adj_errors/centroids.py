#Jane Mills
#11/29/17
#Fix UN pop in centroids

# Import Libraries
import arcpy, os

gridding = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\boundaries\gridding_boundaries_4_1.gdb'
centroids = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\centroids_data\country_data.gdb'

arcpy.env.workspace = gridding
fcList = arcpy.ListFeatureClasses()
fcList.sort()

inFields = ['GUBID','UNE_ATOTPOPBT_2000','UNE_ATOTPOPBT_2005','UNE_ATOTPOPBT_2010','UNE_ATOTPOPBT_2015','UNE_ATOTPOPBT_2020']
outFields = ['GUBID','UN_2000_E','UN_2005_E','UN_2010_E','UN_2015_E','UN_2020_E',
             'UN_2000_DS','UN_2005_DS','UN_2010_DS','UN_2015_DS','UN_2020_DS',
             'TOTAL_A_KM','LAND_A_KM','CONTEXT']

isoList = ['blr','bra','chl','cpv','cub','cyp','ggy','jey','lao','lca','mmr','phl','prk','sau','ssd','uga']

for iso in isoList:
    print iso
    fcPath = os.path.join(gridding,filter(lambda x: iso == x[:3], fcList)[0])
    cenPath = os.path.join(centroids,iso+"_centroids")

    popDict = {}
    with arcpy.da.SearchCursor(fcPath,inFields) as cursor:
        for row in cursor:
            popDict[row[0]] = row[1:]

    with arcpy.da.UpdateCursor(cenPath,outFields) as cursor:
        for row in cursor:
            pop = popDict[row[0]]
            row[1] = pop[0]
            row[2] = pop[1]
            row[3] = pop[2]
            row[4] = pop[3]
            row[5] = pop[4]

            if row[1] == 0:
                row[6:11] = [0]*5
            if row[1] > 0 and row[-2] > 0:
                row[6] = row[1]/row[-2]
                row[7] = row[2]/row[-2]
                row[8] = row[3]/row[-2]
                row[9] = row[4]/row[-2]
                row[10] = row[5]/row[-2]
            if row[1] > 0 and row[-2] == 0:
                row[6] = row[1]/row[-3]
                row[7] = row[2]/row[-3]
                row[8] = row[3]/row[-3]
                row[9] = row[4]/row[-3]
                row[10] = row[5]/row[-3]
                print "found a row with pop and no land:",row[0]
            cursor.updateRow(row)

print 'done'
