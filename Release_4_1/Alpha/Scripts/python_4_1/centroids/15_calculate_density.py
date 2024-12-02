#Jane Mills
#5/31/2017
#Calculate densities

# Import Libraries
import arcpy, os

centroids = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\centroids\country_data.gdb'

cenFields = ['UN_2000_E','UN_2005_E','UN_2010_E','UN_2015_E','UN_2020_E',
             'UN_2000_DS','UN_2005_DS','UN_2010_DS','UN_2015_DS','UN_2020_DS',
             'TOTAL_A_KM','LAND_A_KM','CONTEXT','UBID']

arcpy.env.workspace = centroids
fcList = arcpy.ListFeatureClasses()
fcList.sort()

for fc in fcList:
    print fc[:-10]

    with arcpy.da.UpdateCursor(fc,cenFields) as cursor:
        for row in cursor:
            row[5:10] = [None]*5
            if row[0] == 0:
                row[5] = 0
                row[6] = 0
                row[7] = 0
                row[8] = 0
                row[9] = 0
            if row[0] > 0 and row[-3] > 0:
                row[5] = row[0]/row[-3]
                row[6] = row[1]/row[-3]
                row[7] = row[2]/row[-3]
                row[8] = row[3]/row[-3]
                row[9] = row[4]/row[-3]
            if row[0] > 0 and row[-3] == 0:
                row[5] = row[0]/row[-4]
                row[6] = row[1]/row[-4]
                row[7] = row[2]/row[-4]
                row[8] = row[3]/row[-4]
                row[9] = row[4]/row[-4]
                print "found a row with pop and no land:",row[-1]
                
            cursor.updateRow(row)

print 'done'
